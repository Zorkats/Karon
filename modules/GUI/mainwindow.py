import os
import json
from PySide6.QtCore import Signal, QThread
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QTabWidget, QWidget, QMenu, QMenuBar, QMessageBox, QCheckBox,QDialog, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtGui import QAction, QPixmap, QIcon
from modules.browser.chromium import setup_chromium
from modules.utils import get_base_dir, load_theme
from modules.GUI.settingsdialog import SettingsDialog, SettingsManager
from modules.GUI.download_tab import DownloadTab
from modules.GUI.query_builder_tab import QueryBuilderTab
from modules.GUI.query_optimizer_tab import QueryOptimizerTab
from modules.GUI.wordcloud_tab import WordCloudTab
from modules.GUI.statistics_tab import StatisticsTab

class ChromiumDownloadThread(QThread):
    def run(self):
        setup_chromium()

class MainWindow(QMainWindow):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()

        # Configurar ventana principal
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Karon")
        self.base_dir = get_base_dir()
        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.settings_manager = SettingsManager(self.config_path)
        self.settings_manager.settings_changed.connect(self.apply_settings)
        self.api_input = None  # Inicializar como None en lugar de string vacío
        self.insttoken_input = None
        self.wos_api_input = None
        self.ieee_api_input = None
        self.springer_api_input = None
        self.browser_path_input = None
        self.results_dir_input = None
        self.stealth_checkbox = QCheckBox("Stealth Mode")
        self.scihub_checkbox = QCheckBox("Enable SciHub Downloads")
        
        self.load_config()

        # Crear menú de configuración
        self.create_menu()

        # Crear QTabWidget para las pestañas
        self.tabs = QTabWidget()

        # Añadir pestañas
        self.tabs.addTab(DownloadTab(self.settings_manager), "Download Papers")
        self.tabs.addTab(QueryBuilderTab(self.settings_manager), "Query Builder")
        self.tabs.addTab(QueryOptimizerTab(self.settings_manager), "Query Optimizer")
        self.tabs.addTab(WordCloudTab(), "WordCloud")  # Crear y añadir pestaña WordCloud
        self.tabs.addTab(StatisticsTab(), "Statistics")  # Crear y añadir pestaña Statistics

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.close)


        # Configurar layout principal con pestañas
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()  # Esto empuja el botón hacia la derecha
        exit_layout.addWidget(self.exit_button)
        main_layout.addLayout(exit_layout)
        
        main_container = QWidget()
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

        # Preguntar si el usuario quiere descargar Ungoogled Chromium
        self.ask_for_chromium()

    def create_menu(self):
        """Crear el menú de configuración."""
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        settingsMenu = QMenu("Settings", self)
        self.menuBar.addMenu(settingsMenu)

        # Acción para abrir el diálogo de configuración
        settings_action = QAction("Open Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        settingsMenu.addAction(settings_action)
        
    def load_config(self):
        """Cargar configuraciones desde config.json."""
        if not os.path.exists(self.config_path):
            self.config = {
                "stealth_mode": False,
                "enable_scihub": True,
                "elsevier_api": "",
                "elsevier_insttoken": "",
                "wos_api": "",
                "ieee_api": "",
                "springer_api": "",
                "chromium_path": "",
                "results_dir": "",
                "theme": "Default"
            }
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f)
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

        self.setStyleSheet(load_theme(self.config.get("theme", "")))      
        if not self.config.get("chromium_path"):
            print("Chromium path is not set in the configuration.")

    def ask_for_chromium(self):
        chromium_path = self.config.get("chromium_path", "")
        if not chromium_path or not os.path.exists(chromium_path):
            response = QMessageBox.question(self, "Ungoogled Chromium",
                                            "Ungoogled Chromium no está instalado. ¿Deseas descargarlo?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if response == QMessageBox.StandardButton.Yes:
                self.chromium_thread = ChromiumDownloadThread()
                self.chromium_thread.start()
                print("Downloading Ungoogled Chromium...")
            else:
                print("Defaulting to Playwright.")
        else:
            print("Ungoogled Chromium is already installed!")

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings_manager, self)
        dialog.exec()


    def apply_settings(self, config):
        self.config = config
        if self.api_input:
            self.api_input.setText(self.config.get("elsevier_api", ""))
        if self.insttoken_input:
            self.insttoken_input.setText(self.config.get("elsevier_insttoken", ""))
        if self.wos_api_input:
            self.wos_api_input.setText(self.config.get("wos_api", ""))
        if self.ieee_api_input:
            self.ieee_api_input.setText(self.config.get("ieee_api", ""))
        if self.springer_api_input:
            self.springer_api_input.setText(self.config.get("springer_api", ""))
        if self.browser_path_input:
            self.browser_path_input.setText(self.config.get("chromium_path", ""))
        if self.results_dir_input:
            self.results_dir_input.setText(self.config.get("results_dir", ""))
        self.stealth_checkbox.setChecked(self.config.get("stealth_mode", False))
        self.scihub_checkbox.setChecked(self.config.get("enable_scihub", True))
        
        # Actualizar el tema en tiempo real
        self.setStyleSheet(load_theme(self.config.get("theme", "Default")))
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'update_settings'):
                tab.update_settings(config)



 