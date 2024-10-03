import json
import os

# Leer configuración desde un archivo settings.json
def load_settings():
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    if not os.path.exists(settings_path):
        return {}  # Si no hay archivo de configuración, devuelve un dict vacío
    
    with open(settings_path, 'r') as file:
        return json.load(file)

# Guardar la configuración actualizada en settings.json
def save_settings(settings):
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    
    with open(settings_path, 'w') as file:
        json.dump(settings, file, indent=4)
