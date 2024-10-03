# Karon/pdf_downloader.py
import os
import requests

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

async def download_and_save_pdf_stream(pdf_url, doi, download_folder):
    try:
        download_path = os.path.join(download_folder, f"{doi.replace('/', '_')}.pdf")
        response = requests.get(pdf_url, stream=True, timeout=60)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"PDF guardado en {download_path} para el DOI {doi}")
            return download_path
    except Exception as e:
        print(f"Error al guardar el PDF: {e}")
    return None