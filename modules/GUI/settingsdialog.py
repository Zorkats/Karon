import os
import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QTabWidget, QWidget, QFormLayout, QCheckBox

class SettingsDialog(QDialog):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.config_path = config_path
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
        general_tab.setLayout(general_layout)

        # Pestaña APIs
        api_layout = QFormLayout()
        self.api_input = QLineEdit(self)
        self.api_input.setPlaceholderText("Enter Elsevier API Key")
        self.api_input.setText(self.config.get("elsevier_api", ""))  # Mostrar la API si existe
        api_layout.addRow("Elsevier API:", self.api_input)
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

    def load_config(self):
        """Cargar configuraciones desde config.json o crear con valores por defecto."""
        if not os.path.exists(self.config_path):
            self.config = {
                "stealth_mode": False,
                "elsevier_api": ""
            }
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

    def save_config(self):
        """Guardar las configuraciones en config.json."""
        self.config['stealth_mode'] = self.stealth_checkbox.isChecked()
        self.config['elsevier_api'] = self.api_input.text()

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        self.accept()  # Cerrar el diálogo al guardar
