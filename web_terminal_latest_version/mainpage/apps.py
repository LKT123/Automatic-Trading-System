from django.apps import AppConfig
import threading
from time import sleep
import os
import sys

class MainpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainpage'

    def ready(self):
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true':
                True
                from .Trading_terminal import terminal
                from .backend_manager import BackendManager
                thread = threading.Thread(target=terminal.main, daemon=True)
                # thread.daemon = True  # Optional: makes the thread exit when the main thread exits
                thread.start()
                global terminal_manager
                terminal_manager = BackendManager()
                sleep(30)
                terminal_manager_thread = threading.Thread(target=terminal_manager.auto_update, daemon=True)
                terminal_manager_thread.start()