"""Execução de scripts."""

import time
# Importar pyscreeze explicitamente antes do pyautogui para garantir que esteja disponível
try:
    import pyscreeze
except ImportError:
    # Se não conseguir importar, tentar instalar ou avisar
    pass

import pyautogui
from utils import open_application, resize_window


pyautogui.PAUSE = 0.1 
pyautogui.FAILSAFE = True  


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
    
   
    try:
        test_pos = pyautogui.position()
        if window:
            window.write_event_value('-LOG-', f'PyAutoGUI inicializado. Posição atual do mouse: {test_pos}')
    except Exception as e:
        if window:
            window.write_event_value('-LOG-', f'ERRO: PyAutoGUI não está funcionando: {str(e)}')
        return
    
    if window:
        window.write_event_value('-LOG-', f'Iniciando execução do script: {script_name}')
        window.write_event_value('-LOG-', f'Total de passos: {len(steps)}')
    
    for i, step in enumerate(steps):
        
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
                x, y = int(pos[0]), int(pos[1])
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Tentando clicar em ({x}, {y})...')
                pyautogui.click(x, y)
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: ✓ Clique executado em ({x}, {y})')
            
            elif action_type == 'clique_duplo':
                pos = step.get('position', [0, 0])
                x, y = int(pos[0]), int(pos[1])
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Tentando clique duplo em ({x}, {y})...')
                pyautogui.doubleClick(x, y)
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: ✓ Clique duplo executado em ({x}, {y})')
            
            elif action_type == 'digitar':
                text = step.get('text', '')
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Tentando digitar texto...')
                pyautogui.write(text, interval=0.05)  # Digita com pequeno intervalo entre caracteres
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: ✓ Digitou: "{text[:50]}..."')
            
            elif action_type == 'esperar':
                wait_time = step.get('wait_time', 0)
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Esperando {wait_time}s...')
                time.sleep(wait_time)
            
            elif action_type == 'tecla':
                key = step.get('key', '')
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Tentando pressionar tecla: {key}...')
                pyautogui.press(key)
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: ✓ Tecla {key} pressionada')
            
            elif action_type == 'atalho':
                keys = step.get('keys', [])
                if keys:
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: Tentando atalho: {"+".join(keys)}...')
                    pyautogui.hotkey(*keys)
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: ✓ Atalho {"+".join(keys)} executado')
            
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
            
            elif action_type == 'capturar_tela':
                try:
                    # Verificar se pyscreeze está disponível
                    try:
                        import pyscreeze
                    except ImportError:
                        if window:
                            window.write_event_value('-LOG-', f'Passo {step_label}: ERRO - pyscreeze não está instalado ou não foi incluído no executável!')
                            window.write_event_value('-LOG-', f'Passo {step_label}: Instale com: pip install pyscreeze Pillow')
                        raise ImportError("pyscreeze não está disponível")
                    
                    from config import SCREENSHOTS_DIR
                    import os
                    from datetime import datetime
                    
                    # Obter nome do arquivo
                    screenshot_name = step.get('screenshot_name', '').strip()
                    if not screenshot_name:
                        # Usar timestamp se não fornecido
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        screenshot_name = f'screenshot_{timestamp}'
                    
                    # Garantir extensão .png
                    if not screenshot_name.lower().endswith('.png'):
                        screenshot_name += '.png'
                    
                    # Obter diretório
                    screenshot_dir = step.get('screenshot_dir', '').strip()
                    if not screenshot_dir:
                        screenshot_dir = SCREENSHOTS_DIR
                    
                    # Criar diretório se não existir
                    try:
                        os.makedirs(screenshot_dir, exist_ok=True)
                    except Exception as dir_error:
                        if window:
                            window.write_event_value('-LOG-', f'Passo {step_label}: Aviso - Não foi possível criar diretório {screenshot_dir}: {str(dir_error)}')
                        # Tentar usar diretório padrão
                        screenshot_dir = SCREENSHOTS_DIR
                        os.makedirs(screenshot_dir, exist_ok=True)
                    
                    # Caminho completo do arquivo
                    file_path = os.path.join(screenshot_dir, screenshot_name)
                    
                    # Capturar tela ou região
                    screenshot_region = step.get('screenshot_region', None)
                    if screenshot_region and len(screenshot_region) == 4:
                        # Capturar região específica: [x, y, width, height]
                        x, y, width, height = screenshot_region
                        if window:
                            window.write_event_value('-LOG-', f'Passo {step_label}: Capturando região ({x}, {y}, {width}x{height})...')
                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    else:
                        # Capturar tela inteira
                        if window:
                            window.write_event_value('-LOG-', f'Passo {step_label}: Capturando tela inteira...')
                        screenshot = pyautogui.screenshot()
                    
                    # Salvar arquivo
                    screenshot.save(file_path)
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: ✓ Captura salva em: {file_path}')
                
                except ImportError as e:
                    # Erro de importação - dependência faltando
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: ERRO - Dependência faltando: {str(e)}')
                        window.write_event_value('-LOG-', f'Passo {step_label}: Certifique-se de que pyscreeze e Pillow estão instalados')
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    if window:
                        window.write_event_value('-LOG-', f'Passo {step_label}: ERRO ao capturar tela: {str(e)}')
                        window.write_event_value('-LOG-', f'Passo {step_label}: Detalhes: {error_details[:300]}...')
            
            else:
                if window:
                    window.write_event_value('-LOG-', f'Passo {step_label}: Tipo de ação desconhecido: {action_type}')
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            if window:
                window.write_event_value('-LOG-', f'ERRO no passo {step_label}: {str(e)}')
                window.write_event_value('-LOG-', f'Detalhes: {error_details[:200]}...')
        
    
    if window:
        window.write_event_value('-LOG-', f'Script "{script_name}" executado com sucesso!')
        window.write_event_value('-EXECUTION-FINISHED-', None)

