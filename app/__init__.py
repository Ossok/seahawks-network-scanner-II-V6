from flask import Flask
import threading
import schedule
import time
import json
import os

def create_app():
    app = Flask(__name__)
    
    from .routes import main
    app.register_blueprint(main)
    
    # Charger ou créer la configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump({'target_url': ''}, f)
    
    # Fonction pour planifier l'envoi des données avec contexte
    def schedule_data_sending(app):
        with app.app_context():
            while True:
                schedule.run_pending()
                time.sleep(1)
    
    # Lancer la planification dans un thread séparé avec le contexte
    threading.Thread(target=schedule_data_sending, args=(app,), daemon=True).start()
    
    return app