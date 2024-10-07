# captcha_solver/utils.py
import requests
import os

# Definir base_dir
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
download_path = os.path.join(base_dir, 'downloads')

def get_base_dir():
    """Obtiene el directorio raíz absoluto del proyecto."""
    return base_dir

def get_download_path():
    """Obtiene el directorio de descargas."""
    return download_path


# Función para obtener las credenciales del usuario
def get_credentials():
    credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json')

    if not os.path.exists(credentials_path):
        raise Exception("El archivo de credenciales no existe. Por favor crea credentials.json.")

    import json
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)

    return credentials
