# Karon/pdf_downloader.py
import os
import requests

def is_valid_pdf(content):
    from PyPDF2 import PdfReader
    from io import BytesIO
    try:
        pdf = PdfReader(BytesIO(content))
        return len(pdf.pages) > 0
    except Exception as e:
        print(f"Error al verificar el PDF: {e}")
        return False

def download_pdf_via_api(doi, api_key, elsevier_insttoken=None):
    headers = {}
    url = None
    if doi.startswith('10.1016'):
        headers = {
            'X-ELS-APIKey': api_key,
            'X-ELS-Insttoken': elsevier_insttoken,
            'Accept': 'application/pdf'
        }
        url = f'https://api.elsevier.com/content/article/doi/{doi}'
    elif doi.startswith('10.1007'):
        headers = {
            'Accept': 'application/pdf',
            'api_key': api_key
        }
        url = f'https://api.springer.com/v2/articles/{doi}/fulltext?api_key={api_key}'
    elif doi.startswith('10.1109'):
        headers = {
            'X-API-Key': api_key,
            'Accept': 'application/pdf'
        }
        url = f'https://ieeexploreapi.ieee.org/api/v1/articles/{doi}?apikey={api_key}'

    if url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            if is_valid_pdf(response.content):
                return response.content
            else:
                print(f"El PDF descargado desde la API para {doi} no es válido.")
        return None
    else:
        print(f"DOI {doi} no está soportado por ninguna API.")
        return None


async def download_and_save_pdf_stream(pdf_url, doi, download_path):
    try:
        if not pdf_url.startswith('http'):
            print(f"Advertencia: la URL {pdf_url} no comienza con 'http'. Revisar.")

        # Verificar si la carpeta de descargas existe, y crearla si no.
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)
            print(f"Carpeta creada: {download_path}")

        print(f"Intentando descargar PDF desde URL: {pdf_url}")

        pdf_response = requests.get(pdf_url, stream=True, timeout=30)
        # Verificar si la URL devuelve un PDF válido (código de estado y tipo de contenido)
        if pdf_response.status_code == 200 and 'application/pdf' in pdf_response.headers.get('Content-Type', ''):
            file_path = os.path.join(download_path, f"{doi.replace('/', '_')}.pdf")
            with open(file_path, 'wb') as f:
                for chunk in pdf_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"PDF guardado exitosamente en {file_path} para el DOI {doi}")
            return True  # Retorna True si la descarga fue exitosa
        else:
            print(f"Error al descargar PDF desde URL para DOI {doi}: Código de estado {pdf_response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error al descargar PDF desde URL para DOI {doi}: {e}")
        return False  # Retorna False en caso de error
