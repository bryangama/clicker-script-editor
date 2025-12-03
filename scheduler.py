"""Gerenciamento de agendamento de scripts."""

import time
import schedule
import threading
from script_executor import execute_script


def scheduler_loop(window, stop_event):
    """Loop do agendador em thread separada."""
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)

