import os
import threading
from django.apps import AppConfig
from stock import settings

class StockappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stockapp"
    start_cassandra = False
    ngrok_started = False
    if settings.DB_TYPE == 'cassandra':
        start_cassandra = True
    def ready(self):
        if os.getenv('RUN_MAIN') != 'true':
            return
        from .tasks import schedule_next, start_ngrok
        # Schedule tasks
        schedule_next()
        if StockappConfig.start_cassandra:
            from stockapp.models.crud_operations import close_connection, get_session
            thread = threading.Thread(target=get_session)
            thread.setDaemon(True)
            thread.start()
            import atexit
            atexit.register(close_connection)
            StockappConfig.start_cassandra = False

            ngrok_thread = threading.Thread(target=start_ngrok)
            ngrok_thread.daemon = True
            ngrok_thread.start()
            StockappConfig.ngrok_started = True
        
        
        