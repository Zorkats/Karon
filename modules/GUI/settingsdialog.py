import os
import json
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QTabWidget, QWidget, QFormLayout, QCheckBox, QFileDialog
from modules.utils import get_base_dir

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

    def browse_browser(self):
        """Abrir un diálogo para que el usuario seleccione el navegador."""
        browser_path, _ = QFileDialog.getOpenFileName(self, "Select Chromium Executable", "", "Executables (*.exe)")
        if browser_path:
            self.browser_path_input.setText(browser_path)

    def load_config(self):
        """Cargar configuraciones desde config.json o crear con valores por defecto."""
        if not os.path.exists(self.config_path):
            self.config = {
                "stealth_mode": False,
                "elsevier_api": "",
                "elsevier_insttoken": "",
                "ieee_api": "",
                "springer_api": "",
                "chromium_path": ""
            }
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

    def save_config(self):
        """Guardar las configuraciones en config.json."""
        self.config['stealth_mode'] = self.stealth_checkbox.isChecked()
        self.config['elsevier_api'] = self.api_input.text()
        self.config['elsevier_insttoken'] = self.insttoken_input.text()
        self.config['ieee_api'] = self.ieee_api_input.text()
        self.config['springer_api'] = self.springer_api_input.text()
        self.config['chromium_path'] = self.browser_path_input.text() 

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        self.accept()  # Cerrar el diálogo al guardar
