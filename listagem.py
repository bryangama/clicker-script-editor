"""Aplicativo principal - Editor de Scripts de Cliques."""

import FreeSimpleGUI as sg
import threading
import time
import os
import schedule
from config import DEFAULT_THEME, ALTERNATIVE_THEME, SCRIPTS_DIR
from script_manager import ensure_scripts_dir, load_scripts_list, save_scripts_list, load_script, save_script
from script_executor import execute_script
from gui_components import create_step_dialog, handle_step_dialog_events, create_step_from_dialog
from scheduler import scheduler_loop
from utils import format_step_display, validate_time, get_action_type_key

# Verificar se pyautogui está funcionando corretamente
try:
    import pyautogui
    # Testar se pyautogui consegue obter a posição do mouse
    test_pos = pyautogui.position()
    print(f"PyAutoGUI inicializado corretamente. Posição do mouse: {test_pos}")
except Exception as e:
    print(f"AVISO: PyAutoGUI pode não estar funcionando corretamente: {e}")
    print("O aplicativo pode não conseguir clicar ou interagir com a tela.")


def main():
    """Função principal do aplicativo."""
    # Tema padrão
    current_theme = DEFAULT_THEME
    sg.theme(current_theme)
    
    ensure_scripts_dir()
    scripts_list = load_scripts_list()
    current_script = {'name': '', 'steps': [], 'schedules': []}
    editing_step_index = None
    schedules = []
    
    # Layout principal
    layout = [
        [sg.Text('Montar Script de Cliques', font=('Helvetica', 16, 'bold')),
         sg.Push(),
         sg.Button('Alternar Tema', size=(15, 1), key='-TOGGLE-THEME-', 
                  tooltip=f'Alterna entre {DEFAULT_THEME} e {ALTERNATIVE_THEME}')],
        [sg.HorizontalSeparator()],
        
        [sg.Text('Nome do Script:', size=(15, 1)), 
         sg.Input(key='-SCRIPT-NAME-', size=(30, 1), default_text=current_script['name'])],
        
        [sg.HorizontalSeparator()],
        
        [sg.Text('Passos do Script:', font=('Helvetica', 12, 'bold'))],
        [sg.Listbox(values=[], size=(70, 10), key='-STEPS-LIST-', enable_events=True)],
        
        [sg.Button('Adicionar Passo', size=(15, 1), button_color=('white', 'green')),
         sg.Button('Editar Passo', size=(15, 1)),
         sg.Button('Remover Passo', size=(15, 1), button_color=('white', 'red')),
         sg.Button('Mover para Cima', size=(15, 1)),
         sg.Button('Mover para Baixo', size=(15, 1))],
        
        [sg.HorizontalSeparator()],
        
        [sg.Text('Scripts Salvos:', font=('Helvetica', 12, 'bold'))],
        [sg.Listbox(values=[s.get('name', '') for s in scripts_list], 
                   size=(30, 6), key='-SCRIPTS-LIST-', enable_events=True),
         sg.Column([
             [sg.Button('Carregar Script', size=(20, 1))],
             [sg.Button('Salvar Script', size=(20, 1), button_color=('white', 'blue'))],
             [sg.Button('Deletar Script', size=(20, 1), button_color=('white', 'red'))],
             [sg.Button('Novo Script', size=(20, 1))]
         ])],
        
        [sg.HorizontalSeparator()],
        
        [sg.Text('Agendamento:', font=('Helvetica', 12, 'bold'))],
        [sg.Text('Horário (HH:MM):'), sg.Input(key='-TIME-INPUT-', size=(8, 1)), 
         sg.Button('Add Hora', size=(10, 1))],
        [sg.Listbox(values=schedules, size=(30, 6), key='-SCHEDULES-LIST-', enable_events=True),
         sg.Column([
             [sg.Button('Remover Hora', size=(15, 1))],
             [sg.Checkbox('Ativar Agendamento', key='-SCHEDULE-', enable_events=True, 
                         font=('Helvetica', 10, 'bold'))]
         ])],
        
        [sg.HorizontalSeparator()],
        
        [sg.Text('Status:', size=(8, 1)), 
         sg.Text('Pronto', key='-STATUS-', size=(50, 1))],
        
        [sg.Multiline(size=(70, 6), key='-LOG-', disabled=True, autoscroll=True, 
                     default_text='Log de execução aparecerá aqui...\n')],
        
        [sg.Button('Executar Script', size=(20, 1), button_color=('white', 'green')),
         sg.Button('Parar Execução', size=(20, 1), button_color=('white', '#8B0000'), key='-STOP-BTN-'),
         sg.Push(),
         sg.Button('Sair', size=(10, 1))]
    ]
    
    window = sg.Window('Montar Script de Cliques', layout, finalize=True, disable_close=True)
    
    stop_execution = threading.Event()
    execution_thread = None
    stop_schedule = threading.Event()
    schedule_thread = None
    
    def update_steps_list():
        """Atualiza a lista de passos na interface."""
        steps_display = [format_step_display(step, i) 
                        for i, step in enumerate(current_script['steps'])]
        window['-STEPS-LIST-'].update(steps_display)
    
    def update_scripts_list():
        """Atualiza a lista de scripts salvos."""
        scripts_list = load_scripts_list()
        window['-SCRIPTS-LIST-'].update([s.get('name', '') for s in scripts_list])
        return scripts_list
    
    def log_message(msg):
        """Adiciona mensagem ao log."""
        timestamp = time.strftime("%H:%M:%S")
        window['-LOG-'].update(f'{timestamp} - {msg}\n', append=True)
    
    def update_schedules_list():
        """Atualiza a lista de horários na interface."""
        window['-SCHEDULES-LIST-'].update(schedules)
    
    def start_schedule():
        """Inicia o agendamento do script atual."""
        nonlocal schedule_thread
        
        # Verificar se há passos no script
        if not current_script.get('steps'):
            sg.popup_error('Adicione pelo menos um passo ao script antes de ativar o agendamento!\n\nClique em "Adicionar Passo" para criar passos no script.')
            window['-SCHEDULE-'].update(False)
            return
        
        # Verificar se há horários configurados
        if not schedules:
            sg.popup_error('Adicione pelo menos um horário antes de ativar o agendamento!\n\nDigite um horário no formato HH:MM (ex: 14:30) e clique em "Add Hora".')
            window['-SCHEDULE-'].update(False)
            return
        
        # Limpar agendamentos anteriores
        schedule.clear()
        
        # Criar cópia do script para agendamento
        script_for_schedule = {
            'name': current_script.get('name', 'Script sem nome'),
            'steps': current_script.get('steps', []).copy()
        }
        
        # Validar horários antes de agendar
        valid_times = []
        for time_str in schedules:
            if validate_time(time_str):
                valid_times.append(time_str)
            else:
                sg.popup_error(f'Horário inválido: {time_str}\nUse formato HH:MM (ex: 14:30)')
                window['-SCHEDULE-'].update(False)
                return
        
        if not valid_times:
            sg.popup_error('Nenhum horário válido encontrado!')
            window['-SCHEDULE-'].update(False)
            return
        
        # Agendar execução do script para cada horário válido
        for time_str in valid_times:
            try:
                schedule.every().day.at(time_str).do(execute_script, script_for_schedule, window, None)
            except Exception as e:
                sg.popup_error(f'Erro ao agendar horário {time_str}: {str(e)}')
                window['-SCHEDULE-'].update(False)
                return
        
        # Iniciar thread do agendador
        stop_schedule.clear()
        schedule_thread = threading.Thread(target=scheduler_loop, args=(window, stop_schedule), daemon=True)
        schedule_thread.start()
        
        script_name = current_script.get('name', 'Script sem nome')
        window['-STATUS-'].update(f'Agendamento ATIVO - Script: {script_name}')
        window['-LOG-'].update(f'Agendamento iniciado para o script "{script_name}" nos horários: {", ".join(valid_times)}\n', append=True)
    
    def stop_scheduler():
        """Para o agendamento."""
        stop_schedule.set()
        if schedule_thread:
            schedule_thread.join(timeout=1)
        schedule.clear()
        window['-STATUS-'].update('Agendamento PARADO.')
        window['-LOG-'].update('Agendamento parado.\n', append=True)
    
    def create_main_layout():
        """Cria o layout principal da janela."""
        return [
            [sg.Text('Montar Script de Cliques', font=('Helvetica', 16, 'bold')),
             sg.Push(),
             sg.Button('Alternar Tema', size=(15, 1), key='-TOGGLE-THEME-', 
                      tooltip=f'Alterna entre {DEFAULT_THEME} e {ALTERNATIVE_THEME}')],
            [sg.HorizontalSeparator()],
            
            [sg.Text('Nome do Script:', size=(15, 1)), 
             sg.Input(key='-SCRIPT-NAME-', size=(30, 1), default_text=current_script.get('name', ''))],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('Passos do Script:', font=('Helvetica', 12, 'bold'))],
            [sg.Listbox(values=[], size=(70, 10), key='-STEPS-LIST-', enable_events=True)],
            
            [sg.Button('Adicionar Passo', size=(15, 1), button_color=('white', 'green')),
             sg.Button('Editar Passo', size=(15, 1)),
             sg.Button('Remover Passo', size=(15, 1), button_color=('white', 'red')),
             sg.Button('Mover para Cima', size=(15, 1)),
             sg.Button('Mover para Baixo', size=(15, 1))],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('Scripts Salvos:', font=('Helvetica', 12, 'bold'))],
            [sg.Listbox(values=[s.get('name', '') for s in scripts_list], 
                       size=(30, 6), key='-SCRIPTS-LIST-', enable_events=True),
             sg.Column([
                 [sg.Button('Carregar Script', size=(20, 1))],
                 [sg.Button('Salvar Script', size=(20, 1), button_color=('white', 'blue'))],
                 [sg.Button('Deletar Script', size=(20, 1), button_color=('white', 'red'))],
                 [sg.Button('Novo Script', size=(20, 1))]
             ])],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('Agendamento:', font=('Helvetica', 12, 'bold'))],
            [sg.Text('Horário (HH:MM):'), sg.Input(key='-TIME-INPUT-', size=(8, 1)), 
             sg.Button('Add Hora', size=(10, 1))],
            [sg.Listbox(values=schedules, size=(30, 6), key='-SCHEDULES-LIST-', enable_events=True),
             sg.Column([
                 [sg.Button('Remover Hora', size=(15, 1))],
                 [sg.Checkbox('Ativar Agendamento', key='-SCHEDULE-', enable_events=True, 
                             font=('Helvetica', 10, 'bold'))]
             ])],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('Status:', size=(8, 1)), 
             sg.Text('Pronto', key='-STATUS-', size=(50, 1))],
            
            [sg.Multiline(size=(70, 6), key='-LOG-', disabled=True, autoscroll=True, 
                         default_text='Log de execução aparecerá aqui...\n')],
            
            [sg.Button('Executar Script', size=(20, 1), button_color=('white', 'green')),
             sg.Button('Parar Execução', size=(20, 1), button_color=('white', '#8B0000'), key='-STOP-BTN-'),
             sg.Push(),
             sg.Button('Sair', size=(10, 1))]
        ]
    
    update_steps_list()
    scripts_list = update_scripts_list()
    update_schedules_list()
    
    # Loop principal de eventos
    while True:
        event, values = window.read()
        
        if event == 'Sair':
            break
        
        if event == '-SCRIPT-NAME-':
            current_script['name'] = values['-SCRIPT-NAME-']
        
        if event == 'Novo Script':
            stop_scheduler()
            current_script = {'name': '', 'steps': [], 'schedules': []}
            schedules = []
            window['-SCRIPT-NAME-'].update('')
            window['-STEPS-LIST-'].update([])
            update_schedules_list()
            window['-SCHEDULE-'].update(False)
            window['-STATUS-'].update('Novo script criado')
        
        if event == 'Adicionar Passo':
            dialog = create_step_dialog()
            action_type_key = None
            
            while True:
                d_event, d_values = dialog.read()
                
                if d_event == sg.WIN_CLOSED or d_event == '-CANCEL-':
                    break
                
                action_type_key = handle_step_dialog_events(dialog, d_event, d_values, action_type_key)
                
                if d_event == '-CAPTURE-POS-':
                    x, y = d_values[d_event]
                    dialog['-POS-X-'].update(str(x))
                    dialog['-POS-Y-'].update(str(y))
                    dialog['-STATUS-'].update('Posição capturada!')
                
                if d_event == '-SAVE-':
                    try:
                        action_type_key = get_action_type_key(d_values['-ACTION-TYPE-'])
                        delay = float(d_values['-DELAY-']) if d_values['-DELAY-'] else 0.0
                        step_name = d_values['-STEP-NAME-'].strip()
                        
                        step = create_step_from_dialog(d_values, action_type_key, step_name, delay)
                        current_script['steps'].append(step)
                        
                        update_steps_list()
                        window['-STATUS-'].update('Passo adicionado com sucesso!')
                        break
                    except Exception as e:
                        sg.popup_error(f'Erro ao salvar passo: {e}')
            
            dialog.close()
        
        if event == 'Editar Passo':
            selected = values['-STEPS-LIST-']
            if not selected:
                sg.popup_error('Selecione um passo para editar!')
                continue
            
            index = window['-STEPS-LIST-'].get_indexes()[0]
            editing_step_index = index
            step_data = current_script['steps'][index]
            
            dialog = create_step_dialog(step_data)
            action_type_key = None
            
            while True:
                d_event, d_values = dialog.read()
                
                if d_event == sg.WIN_CLOSED or d_event == '-CANCEL-':
                    editing_step_index = None
                    break
                
                action_type_key = handle_step_dialog_events(dialog, d_event, d_values, action_type_key)
                
                if d_event == '-CAPTURE-POS-':
                    x, y = d_values[d_event]
                    dialog['-POS-X-'].update(str(x))
                    dialog['-POS-Y-'].update(str(y))
                
                if d_event == '-SAVE-':
                    try:
                        action_type_key = get_action_type_key(d_values['-ACTION-TYPE-'])
                        delay = float(d_values['-DELAY-']) if d_values['-DELAY-'] else 0.0
                        step_name = d_values['-STEP-NAME-'].strip()
                        
                        step = create_step_from_dialog(d_values, action_type_key, step_name, delay)
                        current_script['steps'][editing_step_index] = step
                        editing_step_index = None
                        
                        update_steps_list()
                        window['-STATUS-'].update('Passo editado com sucesso!')
                        break
                    except Exception as e:
                        sg.popup_error(f'Erro ao editar passo: {e}')
            
            dialog.close()
        
        if event == 'Remover Passo':
            selected = values['-STEPS-LIST-']
            if not selected:
                sg.popup_error('Selecione um passo para remover!')
                continue
            
            index = window['-STEPS-LIST-'].get_indexes()[0]
            del current_script['steps'][index]
            update_steps_list()
            window['-STATUS-'].update('Passo removido!')
        
        if event == 'Mover para Cima':
            selected = values['-STEPS-LIST-']
            if not selected:
                sg.popup_error('Selecione um passo para mover!')
                continue
            
            index = window['-STEPS-LIST-'].get_indexes()[0]
            if index > 0:
                current_script['steps'][index], current_script['steps'][index-1] = \
                    current_script['steps'][index-1], current_script['steps'][index]
                update_steps_list()
                window['-STEPS-LIST-'].update(set_to_index=[index-1])
        
        if event == 'Mover para Baixo':
            selected = values['-STEPS-LIST-']
            if not selected:
                sg.popup_error('Selecione um passo para mover!')
                continue
            
            index = window['-STEPS-LIST-'].get_indexes()[0]
            if index < len(current_script['steps']) - 1:
                current_script['steps'][index], current_script['steps'][index+1] = \
                    current_script['steps'][index+1], current_script['steps'][index]
                update_steps_list()
                window['-STEPS-LIST-'].update(set_to_index=[index+1])
        
        if event == 'Salvar Script':
            script_name = values['-SCRIPT-NAME-'].strip()
            if not script_name:
                sg.popup_error('Digite um nome para o script!')
                continue
            
            if not current_script['steps']:
                sg.popup_error('Adicione pelo menos um passo ao script!')
                continue
            
            current_script['name'] = script_name
            current_script['schedules'] = schedules.copy()
            save_script(current_script)
            
            # Atualizar lista de scripts
            scripts_list = load_scripts_list()
            script_exists = False
            for i, s in enumerate(scripts_list):
                if s.get('name') == script_name:
                    scripts_list[i] = {'name': script_name}
                    script_exists = True
                    break
            
            if not script_exists:
                scripts_list.append({'name': script_name})
            
            save_scripts_list(scripts_list)
            scripts_list = update_scripts_list()
            window['-STATUS-'].update(f'Script "{script_name}" salvo com sucesso!')
        
        if event == 'Carregar Script':
            selected = values['-SCRIPTS-LIST-']
            if not selected:
                sg.popup_error('Selecione um script para carregar!')
                continue
            
            stop_scheduler()
            
            script_name = selected[0]
            script_data = load_script(script_name)
            
            if script_data:
                current_script = script_data
                schedules = current_script.get('schedules', []).copy()
                window['-SCRIPT-NAME-'].update(current_script.get('name', ''))
                update_steps_list()
                update_schedules_list()
                window['-SCHEDULE-'].update(False)
                window['-STATUS-'].update(f'Script "{script_name}" carregado!')
            else:
                sg.popup_error('Erro ao carregar script!')
        
        if event == 'Deletar Script':
            selected = values['-SCRIPTS-LIST-']
            if not selected:
                sg.popup_error('Selecione um script para deletar!')
                continue
            
            script_name = selected[0]
            if sg.popup_yes_no(f'Deletar o script "{script_name}"?') == 'Yes':
                script_path = os.path.join(SCRIPTS_DIR, f'{script_name}.json')
                if os.path.exists(script_path):
                    os.remove(script_path)
                
                scripts_list = load_scripts_list()
                scripts_list = [s for s in scripts_list if s.get('name') != script_name]
                save_scripts_list(scripts_list)
                scripts_list = update_scripts_list()
                window['-STATUS-'].update(f'Script "{script_name}" deletado!')
        
        if event == 'Executar Script':
            if not current_script.get('steps'):
                sg.popup_error('Adicione pelo menos um passo ao script antes de executar!')
                continue
            
            if execution_thread and execution_thread.is_alive():
                sg.popup_error('Uma execução já está em andamento!')
                continue
            
            # Limpar log anterior
            window['-LOG-'].update('')
            window['-STATUS-'].update('Executando script...')
            window['-STOP-BTN-'].update(button_color=('white', 'red'))
            stop_execution.clear()
            
            # Executar em thread separada
            execution_thread = threading.Thread(
                target=execute_script, 
                args=(current_script, window, stop_execution),
                daemon=True
            )
            execution_thread.start()
        
        if event == '-STOP-BTN-':
            if execution_thread and execution_thread.is_alive():
                stop_execution.set()
                window['-STATUS-'].update('Parando execução...')
                log_message('Solicitação de parada recebida...')
            else:
                window['-STATUS-'].update('Nenhuma execução em andamento!')
        
        if event == 'Add Hora':
            t = values['-TIME-INPUT-'].strip()
            if not t:
                sg.popup_error('Digite um horário no formato HH:MM (ex: 14:30)')
                continue
            
            if validate_time(t):
                if t not in schedules:
                    schedules.append(t)
                    schedules.sort()
                    update_schedules_list()
                    window['-TIME-INPUT-'].update('')
                    window['-STATUS-'].update(f'Horário {t} adicionado! Total: {len(schedules)} horário(s)')
                    current_script['schedules'] = schedules.copy()
                else:
                    sg.popup_error(f'Horário {t} já existe na lista!')
            else:
                sg.popup_error('Formato inválido!\n\nUse o formato HH:MM\nExemplos: 09:00, 14:30, 18:45')
        
        if event == 'Remover Hora':
            selected = values['-SCHEDULES-LIST-']
            if not selected:
                sg.popup_error('Selecione um horário da lista para remover!')
                continue
            
            t = selected[0]
            if t in schedules:
                schedules.remove(t)
                update_schedules_list()
                current_script['schedules'] = schedules.copy()
                window['-STATUS-'].update(f'Horário {t} removido. Total: {len(schedules)} horário(s)')
                
                # Se o agendamento estiver ativo, parar e avisar
                if schedule_thread and schedule_thread.is_alive():
                    sg.popup('Horário removido! O agendamento será reiniciado quando você ativar novamente.', title='Aviso')
                    stop_scheduler()
                    window['-SCHEDULE-'].update(False)
            else:
                sg.popup_error('Horário não encontrado na lista!')
        
        if event == '-SCHEDULE-':
            if values['-SCHEDULE-']:
                start_schedule()
            else:
                stop_scheduler()
        
        if event == '-LOG-':
            msg = values[event]
            log_message(msg)
        
        if event == '-EXECUTION-FINISHED-':
            window['-STOP-BTN-'].update(button_color=('white', '#8B0000'))
            window['-STATUS-'].update('Execução finalizada!')
        
        if event == '-TOGGLE-THEME-':
            # Alternar entre os dois temas
            if current_theme == DEFAULT_THEME:
                current_theme = ALTERNATIVE_THEME
            else:
                current_theme = DEFAULT_THEME
            
            # Aplicar novo tema
            sg.theme(current_theme)
            
            # Salvar estado atual
            script_name = values.get('-SCRIPT-NAME-', '')
            schedule_enabled = values.get('-SCHEDULE-', False)
            log_content = window['-LOG-'].get()
            
            # Atualizar lista de scripts antes de recriar janela
            scripts_list = load_scripts_list()
            
            # Parar scheduler antes de fechar janela (se estiver ativo)
            was_schedule_running = schedule_enabled
            if was_schedule_running:
                stop_scheduler()
            
            # Fechar janela atual
            window.close()
            
            # Recriar layout
            layout = create_main_layout()
            
            # Criar nova janela
            window = sg.Window('Montar Script de Cliques', layout, finalize=True, disable_close=True)
            
            # Restaurar estado
            update_steps_list()
            update_schedules_list()
            window['-LOG-'].update(log_content)
            if was_schedule_running:
                window['-SCHEDULE-'].update(True)
                start_schedule()
            
            window['-STATUS-'].update(f'Tema alterado para {current_theme}!')
            continue  # Continuar loop com nova janela
    
    # Parar execução e agendamento se estiver rodando ao fechar
    stop_scheduler()
    if execution_thread and execution_thread.is_alive():
        stop_execution.set()
    
    window.close()


if __name__ == "__main__":
    main()
