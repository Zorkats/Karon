import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
import shutil
import requests
import zipfile
import os
import platform
import json
from bs4 import BeautifulSoup
from utils import base_dir  # Asegúrate de importar base_dir desde utils

CHROMIUM_FOLDER = os.path.join(base_dir, "Ungoogled Chromium")

# Definir URLs fijas para cada sistema operativo
CHROMIUM_URLS = {
    "windows": "https://ungoogled-software.github.io/ungoogled-chromium-binaries/releases/windows/64bit/",
    "linux": "https://ungoogled-software.github.io/ungoogled-chromium-binaries/releases/appimage/64bit/",
    "mac": "https://ungoogled-software.github.io/ungoogled-chromium-binaries/releases/macos/x86_64/"
}

# Función para detectar el sistema operativo
def get_system_os():
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "mac"
    else:
        return None

# Función para obtener la URL del archivo más reciente en la página de versiones
def get_latest_version_url(system_os):
    base_url = CHROMIUM_URLS.get(system_os)
    if not base_url:
        print(f"No se encontró una URL para {system_os}.")
        return None

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Filtrar los enlaces que terminan en "-1", indicando que es una versión completa
        version_links = [a for a in soup.find_all("a", href=True) if a.text.endswith('-1')]
        if version_links:
            latest_version_url = version_links[0]['href']

            # Extraer solo la parte del número de versión al final de la URL
            version_number = latest_version_url.split('/')[-1]
            # Construir la URL completa
            correct_version_url = base_url.rstrip('/') + '/' + version_number
            return correct_version_url  # Devolver solo la URL con el número de versión correcto
        else:
            print(f"No se encontró un enlace de versión en {base_url}.")
            return None
    except Exception as e:
        print(f"Error obteniendo la URL más reciente: {e}")
        return None

# Función para obtener el enlace al archivo ZIP desde la página de la versión más reciente
def get_latest_zip_url(version_url, system_os):
    try:
        response = requests.get(version_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar el enlace del archivo ZIP para el sistema operativo correspondiente
        if system_os == "windows":
            zip_link = soup.find("a", href=True, text=lambda x: x and 'windows_x64.zip' in x)
        elif system_os == "linux":
            zip_link = soup.find("a", href=True, text=lambda x: x and 'appimage' in x)
        elif system_os == "mac":
            zip_link = soup.find("a", href=True, text=lambda x: x and 'x86_64.zip' in x)
        
        if zip_link:
            zip_url = zip_link['href']

            # Verificar si la URL es relativa y ajustar
            if not zip_url.startswith('http'):
                zip_url = version_url.rstrip('/') + '/' + zip_url.lstrip('/')
            return zip_url
        else:
            print(f"No se encontró un enlace al archivo ZIP en {version_url}.")
            return None
    except Exception as e:
        print(f"Error obteniendo la URL del archivo ZIP: {e}")
        return None

# Función para mover archivos de una subcarpeta al directorio objetivo
def move_files_to_main_folder(extracted_folder):
    for root, dirs, files in os.walk(extracted_folder):
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(CHROMIUM_FOLDER, file)

            # Asegúrate de que los directorios de destino existan
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            try:
                shutil.move(src_path, dest_path)
            except Exception as e:
                print(f"Error moviendo {src_path} a {dest_path}: {e}")

    print("Archivos movidos a la carpeta principal.")

# Función para descargar y extraer el archivo ZIP directamente en CHROMIUM_FOLDER
def download_and_extract_zip(zip_url):
    zip_path = 'chromium.zip'
    print(f"Descargando Ungoogled Chromium desde {zip_url}...")
    
    try:
        with requests.get(zip_url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Extraer directamente en la carpeta base_dir (fuera de Ungoogled Chromium)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(base_dir)

        # Buscar la carpeta dentro del ZIP y mover los archivos a Ungoogled Chromium
        extracted_folder = os.path.join(base_dir, zip_ref.namelist()[0].split('/')[0])
        move_files_to_main_folder(extracted_folder)

        # Eliminar el ZIP y la carpeta extraída
        os.remove(zip_path)
        shutil.rmtree(extracted_folder, ignore_errors=True)

        print("Ungoogled Chromium descargado y extraído con éxito.")
        return True
    except Exception as e:
        print(f"Error descargando o extrayendo el archivo ZIP: {e}")
        return False

# Función para guardar la ruta de chrome.exe en config.json
def save_chromium_path():
    if platform.system() == "Windows":
        chromium_exe_path = os.path.join(CHROMIUM_FOLDER, "chrome.exe")
    else:
        chromium_exe_path = os.path.join(CHROMIUM_FOLDER, "chrome")

    chromium_exe_path = chromium_exe_path.replace('\\', '/')    
    
    if os.path.exists(chromium_exe_path):
        config_path = os.path.join(base_dir, "config.json")
        try:
            with open(config_path, 'r+') as f:
                config = json.load(f)
                config['chromium_path'] = chromium_exe_path
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()
            print(f"Ruta de Chromium guardada en {config_path}: {chromium_exe_path}")
        except Exception as e:
            print(f"Error guardando la ruta de Chromium: {e}")
    else:
        print("No se encontró chrome.exe en la carpeta extraída.")

# Función principal que realiza la instalación o descarga de Chromium
def setup_chromium():
    system_os = get_system_os()
    if not system_os:
        print("Sistema operativo no compatible.")
        return

    # Obtener la URL de la versión más reciente
    version_url = get_latest_version_url(system_os)
    if not version_url:
        return

    # Obtener la URL del archivo ZIP de la versión más reciente
    zip_url = get_latest_zip_url(version_url, system_os)
    if not zip_url:
        return

    # Descargar y extraer el archivo ZIP
    if download_and_extract_zip(zip_url):
        # Guardar la ruta del ejecutable de Chromium en config.json
        save_chromium_path()