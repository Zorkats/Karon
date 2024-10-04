import sys
import os
import json
import csv
import asyncio
import concurrent.futures
from PyQt6.QtCore import QEvent, QCoreApplication, pyqtSignal
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
    log_signal = pyqtSignal(str)  # Usaremos esta señal para actualizar el log

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
        layout.addLayout(csvLayout)
        layout.addWidget(self.logArea)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.beginButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Conectar señales
        self.browseButton.clicked.connect(self.browse_csv)
        self.beginButton.clicked.connect(self.start_downloads)

        # Conectar la señal de log con la función para actualizar la interfaz
        self.log_signal.connect(self.update_log)

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
        self.load_config()

    def browse_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csvPathLine.setText(file_name)

    def start_downloads(self):
        csv_path = self.csvPathLine.text()
        if not csv_path:
            self.log_message("Please provide a valid CSV path.")
            return

        self.log_message("Starting downloads...")

        # Ejecutar en un hilo separado y usar asyncio.run para manejar la función asincrónica
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop.run_in_executor(executor, lambda: asyncio.run(self.process_downloads(csv_path)))

    def log_message(self, message):
        """Emitir señal para actualizar el log de la GUI"""
        self.log_signal.emit(message)

    def update_log(self, message):
        """Agregar un mensaje al log en la GUI"""
        self.logArea.append(message)
        self.logArea.ensureCursorVisible()

    async def process_downloads(self, csv_path):
        try:
            # Crear el BrowserManager y lanzar el navegador
            browser_manager = BrowserManager(executable_path=os.path.join(base_dir, 'Ungoogled Chromium', 'chrome.exe'), headless=True)
            await browser_manager.start_browser()  # Asegúrate de que el navegador se lance correctamente

            if browser_manager.browser is None:
                self.log_message("Error: The browser did not initialize correctly.")
                return  # Detén el proceso si el navegador no se inicializó correctamente

            dois = self.load_dois_from_csv(csv_path)
            total_dois = len(dois)
            self.progressBar.setMaximum(total_dois)

            for index, doi in enumerate(dois):
                self.log_message(f"Processing DOI: {doi}")

                # Asegúrate de que browser_manager.browser no sea None
                if browser_manager.browser:
                    page = await browser_manager.browser.new_page()
                else:
                    self.log_message("Error: Browser is not initialized.")
                    break

                # Intentar descarga con API de Elsevier
                self.log_message(f"Intentando descargar con la API de Elsevier para {doi}...")
                pdf_content = download_pdf_via_api(doi, self.config.get('elsevier_api'))

                if isinstance(pdf_content, str):
                    self.log_message(pdf_content)
                elif pdf_content:
                    self.log_message(f"Downloaded PDF for {doi} via Elsevier API")
                    continue  # Ir al siguiente DOI si la descarga fue exitosa

                # Intentar con selectores avanzados
                self.log_message(f"Intentando descargar con selectores avanzados para {doi}...")
                success = await search_with_advanced_selectors(page, doi, download_path)
                if not success:
                    self.log_message(f"Intentando descargar con el método general para {doi}...")
                    # Intentar con método general
                    success = await search_with_general_method(page, doi, download_path)
                
                if not success:
                    self.log_message(f"Intentando descargar desde Sci-Hub para {doi}...")
                    # Intentar con Sci-Hub
                    success = await download_from_scihub(page, doi, download_path)

                if success:
                    self.log_message(f"Downloaded PDF for {doi} via alternative methods")
                else:
                    self.log_message(f"Failed to download {doi} from all sources")

                # Actualizar barra de progreso
                self.progressBar.setValue(int((index + 1) / total_dois * 100))

            await browser_manager.close_browser()

        except Exception as e:
            self.log_message(f"Error during download: {e}")

    def load_dois_from_csv(self, csv_path):
        dois = []
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                try:
                    doi_index = headers.index("DOI")
                except ValueError:
                    self.log_message("Error: 'DOI' column not found.")
                    return []

                for row in reader:
                    dois.append(row[doi_index])

            return dois

        except Exception as e:
            self.log_message(f"Error reading CSV file: {e}")
            return []
