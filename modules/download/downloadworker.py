import sys
import asyncio
import csv
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
from PyQt6.QtCore import QThread, pyqtSignal
from modules.browser.browser_manager import BrowserManager
from modules.browser.stealth import apply_stealth
from modules.download.pdf_downloader import download_pdf_via_api, download_and_save_pdf_stream
from modules.download.pdf_searcher import search_with_advanced_selectors, search_with_general_method
from modules.download.scihub_downloader import download_from_scihub
from utils import get_download_path

class DownloadWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, csv_path, config, max_concurrent_tasks=3):
        super().__init__()
        self.csv_path = csv_path
        self.config = config
        self.download_path = get_download_path()
        self.max_concurrent_tasks = max_concurrent_tasks  # Número máximo de descargas simultáneas
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.process_downloads())

    async def process_downloads(self):
        """Función principal para manejar las descargas secuenciales."""
        dois = self.load_dois_from_csv(self.csv_path)
        total_dois = len(dois)
    
        self.log_signal.emit("Iniciando navegador...")
        browser_manager = BrowserManager(executable_path=os.path.join(self.config.get('chromium_path')), headless=True)
        await browser_manager.start_browser()
        self.log_signal.emit("Navegador iniciado.")

        # Procesar cada DOI uno por uno secuencialmente
        for index, doi in enumerate(dois):
            await self.download_single_doi(doi, index, total_dois, browser_manager)

        await browser_manager.close_browser()

    async def download_single_doi(self, doi, index, total_dois, browser_manager):
        self.log_signal.emit(f"Processing DOI: {doi}")
        pdf_content = None

        # Intentar descargar con Elsevier
        if doi.startswith("10.1016"):
            self.log_signal.emit(f"Intentando descargar con la API de Elsevier para {doi}...")
            api_key = self.config.get("elsevier_api", None)
            elsevier_insttoken = self.config.get("elsevier_insttoken", None)
            if api_key:
                pdf_content = download_pdf_via_api(doi, api_key, elsevier_insttoken)
                if pdf_content:
                    self.save_pdf(doi, pdf_content, index, total_dois)
                    return  # Si el PDF es válido, terminar la tarea

        # Intentar descargar con Springer
        elif doi.startswith("10.1007"):
            self.log_signal.emit(f"Intentando descargar con la API de Springer para {doi}...")
            api_key = self.config.get("springer_api", None)
            if api_key:
                pdf_content = download_pdf_via_api(doi, api_key)
                if pdf_content:
                    self.save_pdf(doi, pdf_content, index, total_dois)
                    return  # Si el PDF es válido, terminar la tarea

        # Intentar descargar con IEEE
        elif doi.startswith("10.1109"):
            self.log_signal.emit(f"Intentando descargar con la API de IEEE para {doi}...")
            api_key = self.config.get("ieee_api", None)
            if api_key:
                pdf_content = download_pdf_via_api(doi, api_key)
                if pdf_content:
                    self.save_pdf(doi, pdf_content, index, total_dois)
                    return  # Si el PDF es válido, terminar la tarea

        # Si no se usó ninguna API, intentar con navegación web
        apply_stealth_mode = self.config.get("stealth_mode", False)
        page = await browser_manager.new_page()
        if apply_stealth_mode:
            await apply_stealth(page)

        # Navegar a la página del DOI
        url = f"https://doi.org/{doi}"
        self.log_signal.emit(f"Navegando a la página del DOI {doi}...")
        try:
            await page.goto(url, wait_until='load', timeout=60000)
            self.log_signal.emit(f"Navegación a la página del DOI {doi} completada.")
        except Exception as e:
            self.log_signal.emit(f"Error navegando a la página del DOI {doi}: {e}")
            await page.close()
            return

        # Intentar con selectores avanzados
        try:
            self.log_signal.emit(f"Intentando con selectores avanzados para {doi}...")
            pdf_url = await search_with_advanced_selectors(page, doi)
            if pdf_url:
                download_complete = await download_and_save_pdf_stream(pdf_url, doi, self.download_path)
                if download_complete:
                    self.log_signal.emit(f"Downloaded PDF for {doi} via advanced selectors")
                    await page.close()
                    return
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
                    await page.close()
                    return
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
        except Exception as e:
            self.log_signal.emit(f"Error downloading from Sci-Hub for {doi}: {e}")

        await page.close()


    def save_pdf(self, doi, pdf_content, index, total_dois):
        """Guardar el PDF descargado."""
        download_file_path = os.path.join(self.download_path, f"{doi.replace('/', '_')}.pdf")
        with open(download_file_path, 'wb') as f:
            f.write(pdf_content)
        self.log_signal.emit(f"Downloaded PDF for {doi}")
        self.progress_signal.emit(int((index + 1) / total_dois * 100))

    def load_dois_from_csv(self, csv_path):
        """Cargar los DOIs desde un archivo CSV."""
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            doi_index = headers.index("DOI")
            return [row[doi_index] for row in reader]