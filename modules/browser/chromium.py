import os
import platform
import requests
import zipfile
import shutil
from bs4 import BeautifulSoup

# URL base de la página donde se listan las versiones de Ungoogled Chromium
BASE_URL = "https://ungoogled-software.github.io/ungoogled-chromium-binaries/"

# Ruta donde se guardará el navegador descargado
CHROMIUM_FOLDER = os.path.join(os.path.dirname(__file__), "Ungoogled Chromium")

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

# Función para obtener la URL de la versión más reciente
def get_latest_chromium_url(system_os):
    try:
        base_url = "https://ungoogled-software.github.io/ungoogled-chromium-binaries/"
        response = requests.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table_rows = soup.find_all("tr")

        for row in table_rows:
            cells = row.find_all("td")
            if len(cells) > 2:
                os_cell = cells[0].text.strip().lower()
                if system_os in os_cell:
                    download_link = cells[2].find("a")
                    if download_link:
                        return download_link["href"]
                    else:
                        print(f"No download link found in the row for {system_os}.")
            else:
                print(f"Row does not have enough cells: {cells}")
                
        raise Exception(f"No download URL found for {system_os} on the page.")
    
    except Exception as e:
        print(f"Error getting latest Chromium URL: {e}")
        raise

# Función para descargar el navegador si no se encuentra
def download_chromium():
    system_os = get_system_os()

    if system_os is None:
        print("Sistema operativo no compatible.")
        return False

    # Obtener la URL de la versión más reciente
    download_url = get_latest_chromium_url(system_os)

    # Descargar y extraer el archivo ZIP
    zip_path = os.path.join(os.path.dirname(__file__), 'chromium.zip')
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # Extraer archivo ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(CHROMIUM_FOLDER)

    # Eliminar el archivo zip después de extraerlo
    os.remove(zip_path)

    print(f"Ungoogled Chromium descargado y extraído en: {CHROMIUM_FOLDER}")
    return True

# Función para verificar si ya está instalado
def check_chromium_installed():
    chromium_path = os.path.join(CHROMIUM_FOLDER, "chrome.exe")  # Windows
    return os.path.exists(chromium_path)

# Función principal que revisa si está instalado, si no, lo descarga
def setup_chromium():
    if check_chromium_installed():
        print("Ungoogled Chromium ya está instalado.")
    else:
        print("Ungoogled Chromium no está instalado. Descargando...")
        download_chromium()

