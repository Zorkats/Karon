import os
import sys
import pandas as pd
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

def clean_scopus_data(df):
        if df.empty:
            return df
        # Verificar que las columnas esperadas existan
        expected_columns = {
            'dc:title': 'title',
            'dc:creator': 'author',
            'prism:publicationName': 'journal',
            'prism:coverDate': 'year',
            'prism:doi': 'doi'
        }

        # Renombrar columnas si están presentes
        df = df.rename(columns={k: v for k, v in expected_columns.items() if k in df.columns})

        # Seleccionar solo las columnas necesarias
        df = df[[v for v in expected_columns.values() if v in df.columns]]

        # Limpiar la columna de fechas
        if 'year' in df.columns:
            df['year'] = pd.to_datetime(df['year'], errors='coerce').dt.year

        # Eliminar filas con valores nulos en las columnas clave
        df = df.dropna(subset=['title', 'doi'])

        return df

base_dir = get_base_dir()
theme_dir = os.path.join(base_dir, 'themes')
download_path = os.path.join(base_dir, 'downloads')
config_path = os.path.join(base_dir, 'config.json')
