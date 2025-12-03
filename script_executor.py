"""Execução de scripts."""

import time
import pyautogui
from utils import open_application, resize_window


def execute_script(script_data, window=None, stop_event=None):
    """Executa um script completo, passo a passo."""
    if not script_data or 'steps' not in script_data:
        if window:
            window.write_event_value('-LOG-', 'Script vazio ou inválido!')
        return
    
    steps = script_data.get('steps', [])
    if not steps:
        if window:
            window.write_event_value('-LOG-', 'Nenhum passo definido no script!')
        return
    
    script_name = script_data.get('name', 'Script sem nome')
    
    if window:
        window.write_event_value('-LOG-', f'Iniciando execução do script: {script_name}')
        window.write_event_value('-LOG-', f'Total de passos: {len(steps)}')
    
    for i, step in enumerate(steps):
        # Verificar se deve parar
        if stop_event and stop_event.is_set():
            if window:
                window.write_event_value('-LOG-', 'Execução interrompida pelo usuário!')
                window.write_event_value('-EXECUTION-FINISHED-', None)
            return
        
        action_type = step.get('type', 'clique')
        delay = step.get('delay', 0)
        step_name = step.get('name', '')
        step_label = f'"{step_name}"' if step_name else f'{i+1}'
        
        # Esperar o delay antes de executar o passo
        if delay > 0:
            if window:
                window.write_event_value('-LOG-', f'Passo {step_label}: Aguardando {delay}s antes de executar...')
            time.sleep(delay)
        
        try:
            # Executar ação baseada no tipo
            if action_type == 'clique':
                pos = step.get('position', [0, 0])
                pyautogui.click(pos[0], pos[1])
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Clique em ({pos[0]}, {pos[1]})')
            
            elif action_type == 'clique_duplo':
                pos = step.get('position', [0, 0])
                pyautogui.doubleClick(pos[0], pos[1])
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Clique duplo em ({pos[0]}, {pos[1]})')
            
            elif action_type == 'digitar':
                text = step.get('text', '')
                pyautogui.write(text, interval=0.05)  # Digita com pequeno intervalo entre caracteres
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Digitou: "{text[:50]}..."')
            
            elif action_type == 'esperar':
                wait_time = step.get('wait_time', 0)
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Esperando {wait_time}s...')
                time.sleep(wait_time)
            
            elif action_type == 'tecla':
                key = step.get('key', '')
                pyautogui.press(key)
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Pressionou tecla: {key}')
            
            elif action_type == 'atalho':
                keys = step.get('keys', [])
                if keys:
                    pyautogui.hotkey(*keys)
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: Atalho: {"+".join(keys)}')
            
            elif action_type == 'abrir_app':
                app_name = step.get('app_name', '')
                window_size = step.get('window_size', None)
                incognito = step.get('incognito', False)
                try:
                    open_application(app_name, window_size, incognito)
                    size_str = f" ({window_size[0]}x{window_size[1]})" if window_size else ""
                    incognito_str = " em modo anônimo" if incognito else ""
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: Abriu {app_name}{size_str}{incognito_str}')
                except Exception as e:
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: Erro ao abrir {app_name}: {str(e)}')
                    raise
            
            elif action_type == 'redimensionar_janela':
                window_title = step.get('window_title', '')
                size = step.get('size', [800, 600])
                width, height = size[0], size[1]
                try:
                    success = resize_window(window_title, width, height)
                    if success:
                        if window:
                            window.write_event_value('-LOG-', f'Passo {step_label}: Redimensionou "{window_title}" para {width}x{height}')
                    else:
                        if window:
                            window.write_event_value('-LOG-', f'Passo {step_label}: Janela "{window_title}" não encontrada ou erro ao redimensionar')
                except Exception as e:
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: Erro ao redimensionar: {str(e)}')
            
            else:
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Tipo de ação desconhecido: {action_type}')
        
        except Exception as e:
            if window:
                window.write_event_value('-LOG-', f'Erro no passo {step_label}: {str(e)}')
            # Continua para o próximo passo mesmo se houver erro
    
    if window:
        window.write_event_value('-LOG-', f'Script "{script_name}" executado com sucesso!')
        window.write_event_value('-EXECUTION-FINISHED-', None)

