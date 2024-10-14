import os
import json
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QTabWidget, QWidget, QFormLayout, QCheckBox, QFileDialog, QComboBox
from modules.utils import get_base_dir, load_theme, get_available_themes

class SettingsDialog(QDialog):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.base_dir = get_base_dir()
        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)

        self.load_config()

        # Crear un TabWidget para las dos pestañas
        tabs = QTabWidget()
        general_tab = QWidget()
        api_tab = QWidget()

        # Pestaña General
        general_layout = QFormLayout()
        self.stealth_checkbox = QCheckBox("Activate Stealth Mode", self)
        self.stealth_checkbox.setChecked(self.config.get("stealth_mode", False))
        general_layout.addRow(self.stealth_checkbox)

        # Añadir el campo para el "Chromium Path" con un botón "Browse"
        self.browser_path_input = QLineEdit(self)
        self.browser_path_input.setPlaceholderText("Enter Chromium path or browse")
        self.browser_path_input.setText(self.config.get("chromium_path", ""))

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_browser)

        general_layout.addRow("Chromium Path:", self.browser_path_input)
        general_layout.addRow(browse_button)
        general_tab.setLayout(general_layout)

        self.theme_selector = QComboBox(self)
        self.theme_selector.addItems(get_available_themes())
        self.theme_selector.setCurrentText(self.config.get("theme", "default"))
        general_layout.addRow("Theme:", self.theme_selector)

        # Pestaña APIs
        api_layout = QFormLayout()

        self.api_input = QLineEdit(self)
        self.api_input.setPlaceholderText("Enter Elsevier API Key")
        self.api_input.setText(self.config.get("elsevier_api", ""))  # Mostrar la API si existe

        self.insttoken_input = QLineEdit(self)
        self.insttoken_input.setPlaceholderText("Enter Elsevier Insttoken")
        self.insttoken_input.setText(self.config.get("elsevier_insttoken", ""))

        self.ieee_api_input = QLineEdit(self)
        self.ieee_api_input.setPlaceholderText("Enter IEEE API Key")
        self.ieee_api_input.setText(self.config.get("ieee_api", ""))

        self.springer_api_input = QLineEdit(self)
        self.springer_api_input.setPlaceholderText("Enter Springer API Key")
        self.springer_api_input.setText(self.config.get("springer_api", ""))

        api_layout.addRow("Elsevier API:", self.api_input)
        api_layout.addRow("Elsevier Insttoken:", self.insttoken_input)
        api_layout.addRow("IEEE API:", self.ieee_api_input)
        api_layout.addRow("Springer API:", self.springer_api_input)
        api_tab.setLayout(api_layout)

        # Añadir pestañas
        tabs.addTab(general_tab, "General")
        tabs.addTab(api_tab, "APIs")

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)

        # Botón para guardar configuraciones
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_config)
        main_layout.addWidget(save_button)

        self.setLayout(main_layout)

    # Añadir un campo para la carpeta de resultados en SettingsDialog
        self.results_dir_input = QLineEdit(self)
        self.results_dir_input.setPlaceholderText("Select directory to save Query Optimizer results")
        self.results_dir_input.setText(self.config.get("results_dir", ""))
        browse_results_button = QPushButton("Browse")
        browse_results_button.clicked.connect(self.browse_results_dir)

        general_layout.addRow("Results Directory:", self.results_dir_input)
        general_layout.addRow(browse_results_button)


    def browse_browser(self):
        """Abrir un diálogo para que el usuario seleccione el navegador."""
        browser_path, _ = QFileDialog.getOpenFileName(self, "Select Chromium Executable", "", "Executables (*.exe)")
        if browser_path:
            self.browser_path_input.setText(browser_path)

    def browse_results_dir(self):
        """Abrir un diálogo para seleccionar el directorio donde guardar los resultados del Query Optimizer."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.results_dir_input.setText(directory)

    def load_config(self):
        """Cargar configuraciones desde config.json."""
        if not os.path.exists(self.config_path):
            self.config = {
                "stealth_mode": False,
                "elsevier_api": "",
                "elsevier_insttoken": "",
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

        load_theme(self.config.get("theme", ""))
    


    def save_config(self):
        """Guardar las configuraciones en config.json."""
        self.config['stealth_mode'] = self.stealth_checkbox.isChecked()
        self.config['elsevier_api'] = self.api_input.text()
        self.config['elsevier_insttoken'] = self.insttoken_input.text()
        self.config['ieee_api'] = self.ieee_api_input.text()
        self.config['springer_api'] = self.springer_api_input.text()
        self.config['chromium_path'] = self.browser_path_input.text()
        self.config['results_dir'] = self.results_dir_input.text()
        self.config['theme'] = self.theme_selector.currentText()

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        load_theme(self.theme_selector.currentText())

        self.accept()  # Cerrar el diálogo al guardar
