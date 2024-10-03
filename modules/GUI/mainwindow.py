import sys
import os
import asyncio
import csv
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFileDialog, QWidget
from modules.download.pdf_downloader import download_pdf_via_api
from modules.download.scihub_downloader import download_from_scihub
from modules.download.pdf_searcher import search_with_advanced_selectors, search_with_general_method
from modules.browser.browser_manager import BrowserManager
from utils import base_dir
from utils import download_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Karon - Download Papers")
        self.base_dir = base_dir

        # Configurar widgets
        self.csvPathLine = QLineEdit(self)
        self.csvPathLine.setPlaceholderText("Select the .csv with DOIs")
        self.browseButton = QPushButton("Browse", self)
        self.beginButton = QPushButton("Begin Downloads", self)
        self.logArea = QTextEdit(self)
        self.logArea.setReadOnly(True)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.csvPathLine)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.logArea)
        layout.addWidget(self.beginButton)
        layout.addWidget(self.progressBar)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Conectar señales
        self.browseButton.clicked.connect(self.browse_csv)
        self.beginButton.clicked.connect(self.start_downloads)

    def browse_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csvPathLine.setText(file_name)

    def start_downloads(self):
        csv_path = self.csvPathLine.text()
        if not csv_path:
            self.logArea.append("Please provide a valid CSV path.")
            return
        
        self.logArea.append("Starting downloads...")

        # Delegar la lógica a los módulos de descarga
        asyncio.run(self.process_downloads(csv_path))

    async def process_downloads(self, csv_path):
        try:
            # Crear el BrowserManager
            browser_manager = BrowserManager(executable_path=os.path.join(self.base_dir, 'Ungoogled Chromium', 'chrome.exe'), headless=True)
            await browser_manager.start_browser()

            # Cargar DOIs desde el archivo CSV
            dois = self.load_dois_from_csv(csv_path)
            total_dois = len(dois)
            self.progressBar.setMaximum(total_dois)

            for index, doi in enumerate(dois):
                self.logArea.append(f"Processing DOI: {doi}")
                page = await browser_manager.browser.new_page()

                # 1. Intentar descargar con la API de Elsevier
                pdf_content = download_pdf_via_api(doi, "api_key_here")  # Reemplaza con tu clave API
                if pdf_content:
                    self.save_pdf(doi, pdf_content)
                    self.logArea.append(f"Downloaded PDF for {doi} via Elsevier API")
                else:
                    self.logArea.append(f"Failed to download {doi} via API. Trying alternative methods...")

                    # 2. Intentar descargar con selectores avanzados
                    success = await search_with_advanced_selectors(page, doi, download_path)
                    if success:
                        self.logArea.append(f"Downloaded PDF using advanced selectors for {doi}")
                    else:
                        # 3. Si falla, intentar con el método general
                        success = await search_with_general_method(page, doi, download_path)
                        if success:
                            self.logArea.append(f"Downloaded PDF using general method for {doi}")
                        else:
                            # 4. Si todo falla, intentar con Sci-Hub
                            success = await download_from_scihub(page, doi, download_path)
                            if success:
                                self.logArea.append(f"Downloaded PDF via Sci-Hub for {doi}")
                            else:
                                self.logArea.append(f"Failed to download {doi} from all sources")

                # Actualizar progreso
                self.progressBar.setValue(int((index + 1) / total_dois * 100))

                await page.close()

            await browser_manager.close_browser()

        except Exception as e:
            self.logArea.append(f"Error during download: {e}")

    def load_dois_from_csv(self, csv_path):
        dois = []
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)  # Leer la primera fila (los encabezados)
                try:
                    doi_index = headers.index("DOI")
                except ValueError:
                    self.logArea.append("Error: 'DOI' column not found.")
                    return []

                for row in reader:
                    dois.append(row[doi_index])

            return dois

        except Exception as e:
            self.logArea.append(f"Error reading CSV file: {e}")
            return []

    def save_pdf(self, doi, pdf_content):
        file_path = os.path.join(self.base_dir, 'downloads', f"{doi}.pdf")
        try:
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            self.logArea.append(f"PDF saved: {file_path}")
        except Exception as e:
            self.logArea.append(f"Error saving PDF: {e}")
