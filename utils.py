"""Funções utilitárias."""

import os
import sys
import time
import subprocess
import pyautogui
from config import ACTION_TYPES

# Tentar importar pywin32 (opcional)
try:
    import win32gui
    import win32con
    import win32api
    _PYWIN32_AVAILABLE = True
except ImportError:
    _PYWIN32_AVAILABLE = False


def get_mouse_position_after_delay(delay, window):
    """Aguarda alguns segundos e captura a posição do mouse."""
    time.sleep(delay)
    x, y = pyautogui.position()
    window.write_event_value('-CAPTURE-POS-', (x, y))


def find_chrome_path():
    """Encontra o caminho do Google Chrome no sistema."""
    possible_paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        os.path.expanduser(r'~\AppData\Local\Google\Chrome\Application\chrome.exe'),
        'chrome.exe',  # Se estiver no PATH
        'google-chrome',  # Linux
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'  # macOS
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Tentar encontrar via registro do Windows ou PATH
    try:
        if sys.platform == 'win32':
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
            chrome_path = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
            if os.path.exists(chrome_path):
                return chrome_path
    except:
        pass
    
    return None


def get_primary_monitor_position():
    """Obtém a posição do monitor principal (canto superior esquerdo)."""
    if _PYWIN32_AVAILABLE and sys.platform == 'win32':
        try:
            # Usar MonitorFromPoint para encontrar o monitor principal
            # O ponto (0, 0) geralmente está no monitor principal
            monitor = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
            monitor_info = win32api.GetMonitorInfo(monitor)
            work_area = monitor_info['Work']
            primary_x = work_area[0]
            primary_y = work_area[1]
            return primary_x, primary_y
        except Exception:
            # Se falhar, tentar método alternativo
            try:
                # Obter informações do monitor primário usando GetSystemMetrics
                virtual_x = win32api.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
                virtual_y = win32api.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
                
                # O monitor principal geralmente está em (0, 0) ou no início do virtual screen
                primary_x = max(0, virtual_x)
                primary_y = max(0, virtual_y)
                return primary_x, primary_y
            except Exception:
                # Se tudo falhar, retorna (0, 0) que é o padrão do monitor principal
                return 0, 0
    return 0, 0


def open_application(app_name, window_size=None, incognito=False):
    """Abre um aplicativo. Se window_size for fornecido, tenta redimensionar.
    Sempre posiciona na tela principal quando houver múltiplas telas."""
    try:
        if app_name.lower() in ['chrome', 'google chrome', 'google-chrome']:
            chrome_path = find_chrome_path()
            if not chrome_path:
                raise Exception('Google Chrome não encontrado! Instale o Chrome ou especifique o caminho manualmente.')
            
            # Preparar argumentos
            args = [chrome_path]
            if incognito:
                args.append('--incognito')
            if window_size:
                width, height = window_size
                args.extend(['--new-window', f'--window-size={width},{height}'])
            
            # Abrir Chrome
            subprocess.Popen(args, shell=False)
            time.sleep(2)  # Aguardar Chrome abrir
            
            # Sempre tentar posicionar na tela principal usando pywin32
            if _PYWIN32_AVAILABLE:
                time.sleep(2)  # Aguardar mais tempo para garantir que a janela foi criada
                try:
                    # Obter posição do monitor principal
                    primary_x, primary_y = get_primary_monitor_position()
                    
                    # Tentar múltiplas vezes para encontrar a janela do Chrome recém-aberta
                    hwnd = None
                    max_attempts = 8
                    chrome_windows = []
                    
                    for attempt in range(max_attempts):
                        def enum_handler(hwnd, results):
                            if not win32gui.IsWindowVisible(hwnd):
                                return
                            
                            window_text = win32gui.GetWindowText(hwnd).lower()
                            
                            # Procurar por janelas do Chrome
                            # Verificar se é uma janela do Chrome (pode ter "chrome" ou "google" no título)
                            if window_text and ('chrome' in window_text or 'google' in window_text):
                                # Verificar se não é uma janela de popup pequena
                                try:
                                    rect = win32gui.GetWindowRect(hwnd)
                                    width = rect[2] - rect[0]
                                    height = rect[3] - rect[1]
                                    # Janelas muito pequenas provavelmente são popups
                                    if width > 300 and height > 300:
                                        # Verificar se é uma janela de navegador (não popup de extensão)
                                        class_name = win32gui.GetClassName(hwnd)
                                        if 'Chrome' in class_name or 'Chrome_WidgetWin' in class_name:
                                            results.append({
                                                'hwnd': hwnd,
                                                'text': win32gui.GetWindowText(hwnd),
                                                'width': width,
                                                'height': height,
                                                'rect': rect
                                            })
                                except:
                                    pass
                        
                        results = []
                        win32gui.EnumWindows(enum_handler, results)
                        
                        if results:
                            # Ordenar por tamanho (maior primeiro) e pegar a maior janela
                            results.sort(key=lambda x: x['width'] * x['height'], reverse=True)
                            hwnd = results[0]['hwnd']
                            chrome_windows = results
                            break
                        
                        # Aguardar um pouco antes de tentar novamente
                        if attempt < max_attempts - 1:
                            time.sleep(0.5)
                    
                    if hwnd:
                        try:
                            # Obter dimensões atuais da janela
                            rect = win32gui.GetWindowRect(hwnd)
                            current_width = rect[2] - rect[0]
                            current_height = rect[3] - rect[1]
                            
                            # Se especificou tamanho, usar ele; senão manter o tamanho atual
                            if window_size:
                                width, height = window_size
                            else:
                                width, height = current_width, current_height
                            
                            # Sempre usar (0, 0) como coordenada do monitor principal
                            # O monitor principal sempre começa em (0, 0) no sistema de coordenadas do Windows
                            final_x = 0
                            final_y = 0
                            
                            # Primeiro, restaurar a janela se estiver minimizada
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            
                            # Mover e redimensionar na tela principal
                            # Remover flags SWP_NOMOVE para garantir que a janela seja movida
                            win32gui.SetWindowPos(
                                hwnd, 
                                win32con.HWND_TOP, 
                                final_x, 
                                final_y, 
                                width, 
                                height, 
                                win32con.SWP_SHOWWINDOW
                            )
                            
                            # Forçar a janela para o primeiro plano
                            win32gui.SetForegroundWindow(hwnd)
                            
                            # Aguardar um pouco e verificar se a janela foi movida
                            time.sleep(0.2)
                            rect_after = win32gui.GetWindowRect(hwnd)
                            if abs(rect_after[0] - final_x) > 10 or abs(rect_after[1] - final_y) > 10:
                                # Se não foi movida, tentar novamente com MoveWindow
                                win32gui.MoveWindow(hwnd, final_x, final_y, width, height, True)
                        except Exception as e:
                            # Se falhar, tentar método alternativo
                            try:
                                # Tentar mover usando MoveWindow
                                win32gui.MoveWindow(hwnd, primary_x, primary_y, width, height, True)
                            except:
                                pass
                except Exception as e:
                    # Log do erro para debug (pode ser removido depois)
                    pass
            return True
        else:
            subprocess.Popen(app_name, shell=True)
            time.sleep(1)
            return True
    except Exception as e:
        raise Exception(f'Erro ao abrir aplicativo: {str(e)}')


def resize_window(window_title, width, height):
    """Redimensiona uma janela pelo título."""
    try:
        if sys.platform == 'win32':
            if _PYWIN32_AVAILABLE:
                def enum_handler(hwnd, results):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in window_text.lower():
                        results.append(hwnd)
                
                results = []
                win32gui.EnumWindows(enum_handler, results)
                
                if results:
                    hwnd = results[0]
                    # Obter posição atual
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y = rect[0], rect[1]
                    # Redimensionar
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width, height, 
                                        win32con.SWP_SHOWWINDOW)
                    return True
                else:
                    return False
            else:
                # pywin32 não disponível
                return False
        else:
            # Linux/Mac - pode usar wmctrl ou xdotool
            return False
    except Exception:
        return False


def format_step_display(step, index):
    """Formata um passo para exibição na lista."""
    action_type = step.get('type', 'clique')
    delay = step.get('delay', 0)
    step_name = step.get('name', '')
    
    # Se tiver nome, usa ele como prefixo
    name_prefix = f"{step_name} - " if step_name else ""
    
    if action_type == 'clique':
        pos = step.get('position', [0, 0])
        return f"{index+1}. {name_prefix}Clique em ({pos[0]}, {pos[1]}) - Delay: {delay}s"
    elif action_type == 'clique_duplo':
        pos = step.get('position', [0, 0])
        return f"{index+1}. {name_prefix}Clique Duplo em ({pos[0]}, {pos[1]}) - Delay: {delay}s"
    elif action_type == 'digitar':
        text = step.get('text', '')
        return f"{index+1}. {name_prefix}Digitar: '{text[:30]}...' - Delay: {delay}s"
    elif action_type == 'esperar':
        wait_time = step.get('wait_time', 0)
        return f"{index+1}. {name_prefix}Esperar {wait_time}s - Delay: {delay}s"
    elif action_type == 'tecla':
        key = step.get('key', '')
        return f"{index+1}. {name_prefix}Tecla: {key} - Delay: {delay}s"
    elif action_type == 'atalho':
        keys = step.get('keys', [])
        return f"{index+1}. {name_prefix}Atalho: {'+'.join(keys)} - Delay: {delay}s"
    elif action_type == 'abrir_app':
        app_name = step.get('app_name', '')
        window_size = step.get('window_size', None)
        incognito = step.get('incognito', False)
        size_str = f" ({window_size[0]}x{window_size[1]})" if window_size else ""
        incognito_str = " [Modo Anônimo]" if incognito else ""
        return f"{index+1}. {name_prefix}Abrir: {app_name}{size_str}{incognito_str} - Delay: {delay}s"
    elif action_type == 'redimensionar_janela':
        window_title = step.get('window_title', '')
        size = step.get('size', [800, 600])
        return f"{index+1}. {name_prefix}Redimensionar '{window_title}' para {size[0]}x{size[1]} - Delay: {delay}s"
    else:
        return f"{index+1}. {name_prefix}{action_type} - Delay: {delay}s"


def validate_time(time_str):
    """Valida formato de horário HH:MM."""
    import re
    pattern = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def get_action_type_key(value):
    """Converte o valor exibido para a chave do tipo de ação."""
    for key, display_value in ACTION_TYPES.items():
        if display_value == value:
            return key
    return 'clique'

