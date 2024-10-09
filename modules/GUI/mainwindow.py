import os
import json
from PySide6.QtCore import Signal, QThread
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFileDialog, QWidget, QMenu, QMenuBar, QMessageBox, QMenuBar, QFileDialog
from PySide6.QtGui import QAction
from modules.browser.chromium import setup_chromium
from modules.utils import get_base_dir
from modules.GUI.settingsdialog import SettingsDialog
from modules.download.downloadworker import DownloadWorker

class ChromiumDownloadThread(QThread):
    def run(self):
        setup_chromium()

class MainWindow(QMainWindow):
    log_signal = Signal(str)  # Usaremos esta señal para actualizar el log

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Karon")
        self.base_dir = get_base_dir()
        self.config_path = os.path.join(self.base_dir, 'config.json')

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
        self.logArea.setPlaceholderText("Logs will be displayed here.")
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

        # Inicializar señal para logs
        self.worker_log_signal = Signal(str)

        # Cargar configuración
        self.load_config()

        # Preguntar si el usuario quiere descargar Ungoogled Chromium
        self.ask_for_chromium()
        
    def load_config(self):
        """Cargar configuraciones desde config.json."""
        if not os.path.exists(self.config_path):
            self.config = {
                "stealth_mode": False,
                "elsevier_api": "",
                "elsevier_insttoken": "",
                "ieee_api": "",
                "springer_api": "",
                "chromium_path": "" 
            }
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f)
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

        if not self.config.get("chromium_path"):
            self.update_log("Chromium path is not set in the configuration.")

    def ask_for_chromium(self):
        chromium_path = self.config.get("chromium_path", "")

        # Verificar si la ruta está vacía o si el archivo no existe
        if not chromium_path or not os.path.exists(chromium_path):
            response = QMessageBox.question(self, "Ungoogled Chromium",
                                            "Ungoogled Chromium no está instalado. ¿Deseas descargarlo?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if response == QMessageBox.StandardButton.Yes:
                self.chromium_thread = ChromiumDownloadThread()
                self.chromium_thread.start()
                self.update_log("Downloading Ungoogled Chromium...")
            else:
                self.update_log("Defaulting to Playwright.")
        else:
            self.update_log("Ungoogled Chromium is already installed!")

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
            self.update_log("Please provide a valid CSV path.")
            return

        self.update_log("Starting downloads...")

        # Iniciar el proceso de descarga con DownloadWorker
        self.worker = DownloadWorker(csv_path, self.config)
        self.worker.log_signal.connect(self.update_log)  # Conectar los logs al área de texto
        self.worker.progress_signal.connect(self.progressBar.setValue)  # Actualizar la barra de progreso
        self.worker.start()  # Iniciar el worker en un hilo separado

    def update_log(self, message):
        """Actualiza el área de logs en la interfaz gráfica."""
        self.logArea.append(message)