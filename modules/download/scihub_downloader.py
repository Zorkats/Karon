import os
import asyncio
from modules.download.pdf_downloader import download_and_save_pdf_stream

SCI_HUB_URLS = [
    "https://sci-hub.se/",
]

# Función para descargar PDF desde Sci-Hub
async def download_from_scihub(page, doi, download_folder):
    try:
        for sci_hub_url in SCI_HUB_URLS:
            sci_hub_full_url = f"{sci_hub_url}{doi}"
            print(f"Intentando descargar el PDF desde Sci-Hub para el DOI {doi}...")

            # Navegar a la página de Sci-Hub
            response = await page.goto(sci_hub_full_url, wait_until='networkidle', timeout=90000)

            # Verificar si la página de Sci-Hub devuelve un error 404
            if response.status == 404:
                print(f"Error 404: No se encontró el PDF en Sci-Hub para el DOI {doi}. Continuando con el siguiente...")
                return None  # Si es un 404, saltamos al siguiente DOI

            # Verificar si hay contenido (botón 'save' o PDF embebido)
            save_button = await page.query_selector('button[onclick*="location.href"]')
            pdf_embedded = await page.query_selector('embed[type="application/pdf"], iframe[src*=".pdf"]')

            if not save_button and not pdf_embedded:
                print(f"No se encontró contenido en la página de Sci-Hub para el DOI {doi}. Página en blanco.")
                return None  # No hay contenido

            if save_button:
                try:
                    # Esperar y descargar el archivo
                    async with page.expect_download() as download_info:
                        await save_button.click()
                    download = await download_info.value

                    # Guardar el PDF en el directorio de descargas
                    download_path = os.path.join(download_folder, f"{doi.replace('/', '_')}.pdf")
                    await download.save_as(download_path)
                    print(f"PDF descargado exitosamente desde Sci-Hub para el DOI {doi}")
                    return download_path

                except asyncio.TimeoutError:
                    print(f"Timeout esperando el evento de descarga para el DOI {doi}. Verificando si el PDF está embebido...")

            elif pdf_embedded:
                pdf_url = await pdf_embedded.get_attribute('src')
                if pdf_url and pdf_url.startswith('http'):
                    print(f"PDF embebido encontrado en la página para el DOI {doi}. Descargando desde {pdf_url}...")
                    download_complete = download_and_save_pdf_stream(pdf_url, os.path.join(download_folder, f"{doi.replace('/', '_')}.pdf"))
                    if download_complete:
                        return pdf_url

        return None  # Si no se descargó el PDF
    except Exception as e:
        print(f"Error al intentar descargar desde Sci-Hub para el DOI {doi}: {e}")
        return None
