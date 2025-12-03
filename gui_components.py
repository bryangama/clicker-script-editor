"""Componentes de interface gráfica."""

import FreeSimpleGUI as sg
import threading
from config import ACTION_TYPES
from utils import get_mouse_position_after_delay, get_action_type_key


def create_step_dialog(step_data=None):
    """Cria uma janela de diálogo para adicionar/editar um passo."""
    is_edit = step_data is not None
    
    if is_edit:
        action_type = step_data.get('type', 'clique')
        delay = step_data.get('delay', 0)
    else:
        action_type = 'clique'
        delay = 0
    
    layout = [
        [sg.Text('Nome do Passo:', size=(15, 1)), 
         sg.Input(key='-STEP-NAME-', size=(30, 1), 
                 default_text=step_data.get('name', '') if is_edit else '',
                 tooltip='Nome opcional para identificar este passo')],
        
        [sg.Text('Tipo de Ação:', size=(15, 1)), 
         sg.Combo(list(ACTION_TYPES.values()), 
                 default_value=ACTION_TYPES.get(action_type, 'Clique Simples'),
                 key='-ACTION-TYPE-', enable_events=True, size=(20, 1))],
        
        [sg.Text('Delay antes (seg):', size=(15, 1)), 
         sg.Input(default_text=str(delay), key='-DELAY-', size=(10, 1))],
        
        # Campos condicionais baseados no tipo de ação
        [sg.pin(sg.Column([
            [sg.Text('Posição X:', size=(15, 1)), sg.Input(key='-POS-X-', size=(10, 1))],
            [sg.Text('Posição Y:', size=(15, 1)), sg.Input(key='-POS-Y-', size=(10, 1))],
            [sg.Button('Capturar Posição Atual', key='-CAPTURE-BTN-')]
        ], key='-POSITION-FIELDS-', visible=(action_type in ['clique', 'clique_duplo'])))],
        
        [sg.pin(sg.Column([
            [sg.Text('Texto a digitar:', size=(15, 1)), 
             sg.Multiline(key='-TEXT-', size=(30, 3), default_text=step_data.get('text', '') if is_edit else '')]
        ], key='-TEXT-FIELDS-', visible=(action_type == 'digitar')))],
        
        [sg.pin(sg.Column([
            [sg.Text('Tempo de espera (seg):', size=(15, 1)), 
             sg.Input(key='-WAIT-TIME-', size=(10, 1), 
                     default_text=str(step_data.get('wait_time', 0)) if is_edit else '0')]
        ], key='-WAIT-FIELDS-', visible=(action_type == 'esperar')))],
        
        [sg.pin(sg.Column([
            [sg.Text('Tecla:', size=(15, 1)), 
             sg.Input(key='-KEY-', size=(10, 1), 
                     default_text=step_data.get('key', '') if is_edit else '')]
        ], key='-KEY-FIELDS-', visible=(action_type == 'tecla')))],
        
        [sg.pin(sg.Column([
            [sg.Text('Teclas do atalho (separadas por vírgula):', size=(30, 1))],
            [sg.Text('Ex: ctrl, c  ou  alt, tab', size=(30, 1), text_color='gray')],
            [sg.Input(key='-SHORTCUT-KEYS-', size=(30, 1),
                     default_text=','.join(step_data.get('keys', [])) if is_edit and step_data.get('keys') else '')]
        ], key='-SHORTCUT-FIELDS-', visible=(action_type == 'atalho')))],
        
        [sg.pin(sg.Column([
            [sg.Text('Nome do Aplicativo:', size=(15, 1))],
            [sg.Text('Ex: chrome, notepad, calc', size=(30, 1), text_color='gray')],
            [sg.Input(key='-APP-NAME-', size=(30, 1),
                     default_text=step_data.get('app_name', 'chrome') if is_edit else 'chrome')],
            [sg.Checkbox('Modo Anônimo (Incognito)', key='-INCOGNITO-', 
                        default=step_data.get('incognito', False) if is_edit else False,
                        tooltip='Abre o Chrome em modo anônimo (apenas para Chrome)')],
            [sg.Text('Largura:', size=(8, 1)), sg.Input(key='-WIDTH-', size=(8, 1), 
                     default_text=str(step_data.get('window_size', [800, 600])[0]) if is_edit and step_data.get('window_size') else '800')],
            [sg.Text('Altura:', size=(8, 1)), sg.Input(key='-HEIGHT-', size=(8, 1),
                     default_text=str(step_data.get('window_size', [800, 600])[1]) if is_edit and step_data.get('window_size') else '600')],
            [sg.Text('Deixe vazio para tamanho padrão', size=(30, 1), text_color='gray', font=('Helvetica', 8))]
        ], key='-APP-FIELDS-', visible=(action_type == 'abrir_app')))],
        
        [sg.pin(sg.Column([
            [sg.Text('Título da Janela:', size=(15, 1))],
            [sg.Text('Ex: Google Chrome, Notepad', size=(30, 1), text_color='gray')],
            [sg.Input(key='-WINDOW-TITLE-', size=(30, 1),
                     default_text=step_data.get('window_title', 'Google Chrome') if is_edit else 'Google Chrome')],
            [sg.Text('Largura:', size=(8, 1)), sg.Input(key='-RESIZE-WIDTH-', size=(8, 1),
                     default_text=str(step_data.get('size', [800, 600])[0]) if is_edit and step_data.get('size') else '800')],
            [sg.Text('Altura:', size=(8, 1)), sg.Input(key='-RESIZE-HEIGHT-', size=(8, 1),
                     default_text=str(step_data.get('size', [800, 600])[1]) if is_edit and step_data.get('size') else '600')]
        ], key='-RESIZE-FIELDS-', visible=(action_type == 'redimensionar_janela')))],
        
        [sg.Text('', key='-STATUS-', size=(40, 1), text_color='blue')],
        
        [sg.Button('Salvar', key='-SAVE-'), sg.Button('Cancelar', key='-CANCEL-')]
    ]
    
    dialog = sg.Window('Adicionar/Editar Passo', layout, modal=True, finalize=True)
    
    # Preencher campos se estiver editando
    if is_edit:
        if action_type in ['clique', 'clique_duplo']:
            pos = step_data.get('position', [0, 0])
            dialog['-POS-X-'].update(str(pos[0]))
            dialog['-POS-Y-'].update(str(pos[1]))
        elif action_type == 'abrir_app':
            dialog['-APP-NAME-'].update(step_data.get('app_name', 'chrome'))
            dialog['-INCOGNITO-'].update(step_data.get('incognito', False))
            window_size = step_data.get('window_size', None)
            if window_size:
                dialog['-WIDTH-'].update(str(window_size[0]))
                dialog['-HEIGHT-'].update(str(window_size[1]))
        elif action_type == 'redimensionar_janela':
            dialog['-WINDOW-TITLE-'].update(step_data.get('window_title', 'Google Chrome'))
            size = step_data.get('size', [800, 600])
            dialog['-RESIZE-WIDTH-'].update(str(size[0]))
            dialog['-RESIZE-HEIGHT-'].update(str(size[1]))
    
    return dialog


def handle_step_dialog_events(dialog, d_event, d_values, action_type_key):
    """Processa eventos do diálogo de passo."""
    if d_event == '-ACTION-TYPE-':
        action_type_key = get_action_type_key(d_values['-ACTION-TYPE-'])
        dialog['-POSITION-FIELDS-'].update(visible=(action_type_key in ['clique', 'clique_duplo']))
        dialog['-TEXT-FIELDS-'].update(visible=(action_type_key == 'digitar'))
        dialog['-WAIT-FIELDS-'].update(visible=(action_type_key == 'esperar'))
        dialog['-KEY-FIELDS-'].update(visible=(action_type_key == 'tecla'))
        dialog['-SHORTCUT-FIELDS-'].update(visible=(action_type_key == 'atalho'))
        dialog['-APP-FIELDS-'].update(visible=(action_type_key == 'abrir_app'))
        dialog['-RESIZE-FIELDS-'].update(visible=(action_type_key == 'redimensionar_janela'))
    
    if d_event == '-CAPTURE-BTN-':
        dialog['-STATUS-'].update('Aguardando 3 segundos... Posicione o mouse onde deseja clicar.')
        threading.Thread(target=get_mouse_position_after_delay, 
                        args=(3, dialog), daemon=True).start()
    
    return action_type_key


def create_step_from_dialog(d_values, action_type_key, step_name, delay):
    """Cria um dicionário de passo a partir dos valores do diálogo."""
    step = {'type': action_type_key, 'delay': delay}
    if step_name:
        step['name'] = step_name
    
    if action_type_key in ['clique', 'clique_duplo']:
        x = int(d_values['-POS-X-']) if d_values['-POS-X-'] else 0
        y = int(d_values['-POS-Y-']) if d_values['-POS-Y-'] else 0
        step['position'] = [x, y]
    elif action_type_key == 'digitar':
        step['text'] = d_values['-TEXT-']
    elif action_type_key == 'esperar':
        step['wait_time'] = float(d_values['-WAIT-TIME-']) if d_values['-WAIT-TIME-'] else 0.0
    elif action_type_key == 'tecla':
        step['key'] = d_values['-KEY-']
    elif action_type_key == 'atalho':
        keys_str = d_values['-SHORTCUT-KEYS-']
        step['keys'] = [k.strip() for k in keys_str.split(',') if k.strip()]
    elif action_type_key == 'abrir_app':
        app_name = d_values['-APP-NAME-'].strip() or 'chrome'
        step['app_name'] = app_name
        step['incognito'] = d_values.get('-INCOGNITO-', False)
        width_str = d_values.get('-WIDTH-', '').strip()
        height_str = d_values.get('-HEIGHT-', '').strip()
        if width_str and height_str:
            try:
                width = int(width_str)
                height = int(height_str)
                step['window_size'] = [width, height]
            except ValueError:
                pass
    elif action_type_key == 'redimensionar_janela':
        window_title = d_values['-WINDOW-TITLE-'].strip() or 'Google Chrome'
        step['window_title'] = window_title
        width_str = d_values.get('-RESIZE-WIDTH-', '800').strip()
        height_str = d_values.get('-RESIZE-HEIGHT-', '600').strip()
        try:
            width = int(width_str) if width_str else 800
            height = int(height_str) if height_str else 600
            step['size'] = [width, height]
        except ValueError:
            step['size'] = [800, 600]
    
    return step

