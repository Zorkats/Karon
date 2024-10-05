import asyncio
import csv
import os
from PyQt6.QtCore import QThread, pyqtSignal
from modules.browser.browser_manager import BrowserManager
from modules.browser.stealth import apply_stealth
from modules.download.pdf_downloader import download_pdf_via_api, download_and_save_pdf_stream
from modules.download.pdf_searcher import search_with_advanced_selectors, search_with_general_method
from modules.download.scihub_downloader import download_from_scihub
from utils import get_download_path
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
        dois = self.load_dois_from_csv(self.csv_path)  # Llamar a la función simplificada para cargar los DOIs
        total_dois = len(dois)
    
        # Iniciar el navegador con modo sigiloso si está activado
        self.log_signal.emit("Iniciando navegador...")
        browser_manager = BrowserManager(executable_path=os.path.join(self.config.get('chromium_path')), headless=True)
        await browser_manager.start_browser()
        self.log_signal.emit("Navegador iniciado.")

        for index, doi in enumerate(dois):
            self.log_signal.emit(f"Processing DOI: {doi}")

            # Intentar descargar con API de Elsevier
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
                    continue

            # Crear una nueva página en el navegador
            self.log_signal.emit("Creando nueva página en el navegador...")
            page = await browser_manager.browser.new_page()
            self.log_signal.emit("Página creada exitosamente.")

            # Navegar a la página del DOI
            url = f"https://doi.org/{doi}"
            self.log_signal.emit(f"Navegando a la página del DOI {doi}...")
            try:
                await page.goto(url, wait_until='load', timeout=60000)
                self.log_signal.emit(f"Navegación a la página del DOI {doi} completada.")
            except Exception as e:
                self.log_signal.emit(f"Error navegando a la página del DOI {doi}: {e}")
                continue

            # Intentar con selectores avanzados
            try:
                self.log_signal.emit(f"Intentando con selectores avanzados para {doi}...")
                pdf_url = await search_with_advanced_selectors(page, doi)
                if pdf_url:
                    download_complete = await download_and_save_pdf_stream(pdf_url, doi, self.download_path)
                    if download_complete:
                        self.log_signal.emit(f"Downloaded PDF for {doi} via advanced selectors")
                        self.progress_signal.emit(int((index + 1) / total_dois * 100))
                        await page.close()
                        continue  # Si se descarga correctamente, pasar al siguiente DOI
                else:
                    self.log_signal.emit(f"No se encontró PDF con selectores avanzados para {doi}")
            except Exception as e:
                self.log_signal.emit(f"Error in advanced selectors for {doi}: {e}")

            # Intentar con el método general
            try:
                self.log_signal.emit(f"Intentando con el método general para {doi}...")
                pdf_url = await search_with_general_method(page, doi)
                if pdf_url:
                    download_complete = await download_and_save_pdf_stream(pdf_url, doi, self.download_path)
                    if download_complete:
                        self.log_signal.emit(f"Downloaded PDF for {doi} via general method")
                        self.progress_signal.emit(int((index + 1) / total_dois * 100))
                        await page.close()
                        continue  # Si se descarga correctamente, pasar al siguiente DOI
                else:
                    self.log_signal.emit(f"No se encontró PDF con el método general para {doi}")
            except Exception as e:
                self.log_signal.emit(f"Error in general method for {doi}: {e}")

            # Si fallan los métodos avanzados y general, intentar con Sci-Hub
            try:
                self.log_signal.emit(f"Intentando descargar desde Sci-Hub para {doi}...")
                success = await download_from_scihub(page, doi, self.download_path)
                if success:
                    self.log_signal.emit(f"Downloaded PDF for {doi} via Sci-Hub")
                else:
                    self.log_signal.emit(f"Failed to download {doi} from all sources")
                self.progress_signal.emit(int((index + 1) / total_dois * 100))
                await page.close()
            except Exception as e:
                self.log_signal.emit(f"Error downloading from Sci-Hub for {doi}: {e}")

        self.log_signal.emit("Cerrando navegador...")
        await browser_manager.close_browser()
        self.log_signal.emit("Navegador cerrado.")

    # Método simplificado para cargar DOIs desde un CSV
    def load_dois_from_csv(self, csv_path):
        """Cargar los DOIs desde un archivo CSV."""
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            doi_index = headers.index("DOI")  # Asumiendo que la columna se llama "DOI"
            dois = [row[doi_index] for row in reader]
        self.log_signal.emit(f"DOIs cargados exitosamente desde {csv_path}")
        return dois