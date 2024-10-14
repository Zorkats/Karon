import os
import sys
from PySide6.QtWidgets import QApplication

def get_base_dir():
    if getattr(sys, 'frozen', False):
    # Si el programa está congelado (por ejemplo, al ejecutar el .exe generado)
        return os.path.dirname(sys.argv[0])
    else:
        # Si el programa está en modo script (por ejemplo, en desarrollo)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
def get_download_path():
    """Obtiene el directorio de descargas."""
    return download_path

def get_available_themes():
    if not os.path.exists(theme_dir):
        os.makedirs(theme_dir)
    return [f.replace('.qss', '') for f in os.listdir(theme_dir) if f.endswith('.qss')]

def load_theme(theme_name):
    """Cargar y aplicar el tema desde la carpeta themes."""
    theme_path = os.path.join(theme_dir, f"{theme_name}.qss")
    if os.path.exists(theme_path):
        with open(theme_path, 'r') as f:
            theme = f.read()
            QApplication.instance().setStyleSheet(theme)

base_dir = get_base_dir()
theme_dir = os.path.join(base_dir, 'themes')
download_path = os.path.join(base_dir, 'downloads')
config_path = os.path.join(base_dir, 'config.json')
