import asyncio
import csv
import os
from PyQt6.QtCore import QThread, pyqtSignal
from modules.browser.browser_manager import BrowserManager
from modules.browser.stealth import apply_stealth
from modules.download.pdf_downloader import download_pdf_via_api
from modules.download.pdf_searcher import search_with_advanced_selectors, search_with_general_method
from modules.download.scihub_downloader import download_from_scihub
from utils import get_download_path  # Usamos get_download_path directamente
import json

class DownloadWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, csv_path, config):
        super().__init__()
        self.csv_path = csv_path
        self.config = config  # Pasar la configuración desde mainwindow.py
        self.download_path = get_download_path()  # Obtener la ruta de descargas desde utils.py

    def run(self):
        """Iniciar el proceso de descargas en un hilo separado."""
        loop = asyncio.new_event_loop()  # Crear un nuevo ciclo de eventos
        asyncio.set_event_loop(loop)  # Establecer el ciclo de eventos
        loop.run_until_complete(self.process_downloads())  # Ejecutar descargas en el ciclo asincrónico

    async def process_downloads(self):
        """Función principal para manejar las descargas asincrónicas."""
        dois = self.load_dois_from_csv(self.csv_path)
        total_dois = len(dois)

        # Iniciar el navegador con modo sigiloso si está activado
        browser_manager = BrowserManager(executable_path=os.path.join(self.config.get('chromium_path')), headless=True)
        await browser_manager.start_browser()

        for index, doi in enumerate(dois):
            self.log_signal.emit(f"Processing DOI: {doi}")

            # Crear una nueva página para cada DOI
            page = await browser_manager.browser.new_page()

            # Aplicar el modo sigiloso si está activado
            if self.config.get("stealth_mode", False):
                await apply_stealth(page)

            # Intentar descargar el PDF con la API de Elsevier
            self.log_signal.emit(f"Intentando descargar con la API de Elsevier para {doi}...")
            api_key = self.config.get("elsevier_api", "")
            if api_key:
                pdf_content = download_pdf_via_api(doi, api_key)
                if pdf_content:
                    download_file_path = os.path.join(self.download_path, f"{doi.replace('/', '_')}.pdf")
                    with open(download_file_path, 'wb') as f:
                        f.write(pdf_content)
                    self.log_signal.emit(f"Downloaded PDF for {doi} via Elsevier API")
                    self.progress_signal.emit(int((index + 1) / total_dois * 100))
                    await page.close()  # Cierra la página antes de continuar al siguiente DOI
                    continue  # Pasar al siguiente DOI si se descargó con éxito

            # Si la API falla, intentar con selectores avanzados
            try:
                success = await search_with_advanced_selectors(page, doi, self.download_path)
                if success:
                    self.log_signal.emit(f"Downloaded PDF for {doi} via advanced selectors")
                    self.progress_signal.emit(int((index + 1) / total_dois * 100))
                    await page.close()  # Cierra la página antes de continuar
                    continue
            except Exception as e:
                self.log_signal.emit(f"Error in advanced selectors for {doi}: {e}")

            # Si fallan los selectores avanzados, intentar con el método general
            try:
                success = await search_with_general_method(page, doi, self.download_path)
                if success:
                    self.log_signal.emit(f"Downloaded PDF for {doi} via general method")
                    self.progress_signal.emit(int((index + 1) / total_dois * 100))
                    await page.close()  # Cierra la página antes de continuar
                    continue
            except Exception as e:
                self.log_signal.emit(f"Error in general method for {doi}: {e}")

            # Si fallan todos los métodos anteriores, intentar con Sci-Hub
            try:
                success = await download_from_scihub(page, doi, self.download_path)
                if success:
                    self.log_signal.emit(f"Downloaded PDF for {doi} via Sci-Hub")
                else:
                    self.log_signal.emit(f"Failed to download {doi} from all sources")
                self.progress_signal.emit(int((index + 1) / total_dois * 100))
                await page.close()  # Cierra la página antes de continuar
            except Exception as e:
                self.log_signal.emit(f"Error downloading from Sci-Hub for {doi}: {e}")
                await page.close()

        await browser_manager.close_browser()


    def load_dois_from_csv(self, csv_path):
        """Cargar los DOIs desde un archivo CSV."""
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            doi_index = headers.index("DOI")
            dois = [row[doi_index] for row in reader]
        return dois
