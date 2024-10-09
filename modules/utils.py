import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
    # Si el programa está congelado (por ejemplo, al ejecutar el .exe generado)
        return os.path.dirname(sys.argv[0])
    else:
        # Si el programa está en modo script (por ejemplo, en desarrollo)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

base_dir = get_base_dir()
download_path = os.path.join(base_dir, 'downloads')
config_path = os.path.join(base_dir, 'config.json')

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
