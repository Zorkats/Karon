# Karon/pdf_downloader.py
import os
import requests
import aiohttp
from utils import save_pdf_directly, get_download_path

def is_valid_pdf(content):
    from PyPDF2 import PdfReader
    from io import BytesIO
    try:
        pdf = PdfReader(BytesIO(content))
        return len(pdf.pages) > 1
    except Exception as e:
        print(f"Error al verificar el PDF: {e}")
        return False

def download_pdf_via_api(doi, api_key):
    headers = {
        'X-ELS-APIKey': api_key,
        'Accept': 'application/pdf',
    }
    url = f'https://api.elsevier.com/content/article/doi/{doi}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
        if is_valid_pdf(response.content):
            return response.content
        else:
            print(f"El PDF descargado desde la API de Elsevier para {doi} no es válido.")
    return None

async def download_and_save_pdf_stream(pdf_url, doi):
    # Obtener la ruta completa de descarga directamente usando get_download_path()
    download_path = os.path.join(get_download_path(), f"{doi.replace('/', '_')}.pdf")
    
    try:
        # Crear sesión para manejar la descarga del PDF
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                    pdf_content = await response.read()  # Leer el contenido del PDF
                    
                    # Usar la función save_pdf_directly para guardar el PDF
                    save_pdf_directly(pdf_content, download_path)
                    
                    print(f"PDF guardado en {download_path} para el DOI {doi}")
                    return download_path
                else:
                    print(f"No se pudo descargar el PDF para {doi}. Código de estado: {response.status}")
    except Exception as e:
        print(f"Error al guardar el PDF para {doi}: {e}")
    return None