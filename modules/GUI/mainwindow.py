import sys
import os
import json
import asyncio
import csv
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFileDialog, QWidget, QMenu, QMenuBar
from PyQt6.QtGui import QAction
from modules.browser.browser_manager import BrowserManager
from modules.browser.stealth import apply_stealth
from modules.download.pdf_downloader import download_pdf_via_api
from modules.download.pdf_searcher import search_with_advanced_selectors, search_with_general_method
from modules.download.scihub_downloader import download_from_scihub
from utils import base_dir, download_path
from modules.GUI.settingsdialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Karon - Download Papers")
        self.base_dir = base_dir
        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.load_config()

        # Crear menú de configuración
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        settingsMenu = QMenu("Settings", self)
        self.menuBar.addMenu(settingsMenu)

        # Acción para abrir el diálogo de configuración
        settings_action = QAction("Open Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        settingsMenu.addAction(settings_action)

        # Configurar widgets
        self.csvPathLine = QLineEdit(self)
        self.csvPathLine.setPlaceholderText("Select the .csv with DOIs")
        self.browseButton = QPushButton("Browse", self)
        self.beginButton = QPushButton("Begin Downloads", self)
        self.logArea = QTextEdit(self)
        self.logArea.setReadOnly(True)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)

        # Crear layout horizontal para la barra CSV y el botón de Browse
        csvLayout = QHBoxLayout()
        csvLayout.addWidget(self.csvPathLine)
        csvLayout.addWidget(self.browseButton)

        # Crear layout vertical para organizar los widgets
        layout = QVBoxLayout()
        layout.addLayout(csvLayout)  # Añadir el layout horizontal al layout principal
        layout.addWidget(self.logArea)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.beginButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Conectar señales
        self.browseButton.clicked.connect(self.browse_csv)
        self.beginButton.clicked.connect(self.start_downloads)

    def load_config(self):
        """Cargar configuraciones desde config.json."""
        if not os.path.exists(self.config_path):
            self.config = {
                "stealth_mode": False,
                "elsevier_api": ""
            }
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f)
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.config_path, self)
        dialog.exec()

        # Recargar configuraciones tras cerrar el diálogo
        self.load_config()

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

        if self.config.get("stealth_mode", False):
            self.logArea.append("Stealth mode activated...")

        asyncio.run(self.process_downloads(csv_path))

    async def process_downloads(self, csv_path):
        try:
            browser_manager = BrowserManager(executable_path=os.path.join(self.base_dir, 'Ungoogled Chromium', 'chrome.exe'), headless=True)
            await browser_manager.start_browser()

            dois = self.load_dois_from_csv(csv_path)
            total_dois = len(dois)
            self.progressBar.setMaximum(total_dois)

            for index, doi in enumerate(dois):
                self.logArea.append(f"Processing DOI: {doi}")
                page = await browser_manager.browser.new_page()

                # Lógica de descarga delegada a los módulos
                if self.config.get("elsevier_api", ""):
                    pdf_content = download_pdf_via_api(doi, self.config["elsevier_api"])
                    if pdf_content:
                        self.logArea.append(f"Downloaded PDF for {doi} via Elsevier API")
                else:
                    success = await search_with_advanced_selectors(page, doi, download_path)
                    if success:
                        self.logArea.append(f"Downloaded PDF using advanced selectors for {doi}")
                    else:
                        success = await search_with_general_method(page, doi, download_path)
                        if success:
                            self.logArea.append(f"Downloaded PDF using general method for {doi}")
                        else:
                            success = await download_from_scihub(page, doi, download_path)
                            if success:
                                self.logArea.append(f"Downloaded PDF via Sci-Hub for {doi}")
                            else:
                                self.logArea.append(f"Failed to download {doi} from all sources")

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
                headers = next(reader)
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
