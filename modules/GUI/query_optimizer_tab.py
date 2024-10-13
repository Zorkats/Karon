from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog
from modules.download.query_optimizer import combine_queries, clean_data, filter_by_keyword, save_data, generate_report

class QueryOptimizerTab(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar widgets
        self.scopus_path_input = QLineEdit(self)
        self.scopus_path_input.setPlaceholderText("Scopus CSV Path")
        self.browse_scopus_button = QPushButton("Browse", self)
        self.wos_path_input = QLineEdit(self)
        self.wos_path_input.setPlaceholderText("WoS CSV Path")
        self.browse_wos_button = QPushButton("Browse", self)
        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Enter keyword to filter results")
        self.optimize_button = QPushButton("Run Query Optimizer", self)

        # Crear layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.scopus_path_input)
        layout.addWidget(self.browse_scopus_button)
        layout.addWidget(self.wos_path_input)
        layout.addWidget(self.browse_wos_button)
        layout.addWidget(self.keyword_input)
        layout.addWidget(self.optimize_button)

        self.setLayout(layout)

        # Conectar señales
        self.browse_scopus_button.clicked.connect(self.browse_scopus)
        self.browse_wos_button.clicked.connect(self.browse_wos)
        self.optimize_button.clicked.connect(self.run_query_optimizer)

    def browse_scopus(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Scopus CSV", "", "CSV Files (*.csv)")
        if file_name:
            self.scopus_path_input.setText(file_name)

    def browse_wos(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select WoS CSV", "", "CSV Files (*.csv)")
        if file_name:
            self.wos_path_input.setText(file_name)

    def run_query_optimizer(self):
        scopus_path = self.scopus_path_input.text()
        wos_path = self.wos_path_input.text()
        keyword = self.keyword_input.text()

        if not scopus_path:
            self.update_log("Please provide a Scopus CSV path.")
            return

        df_combined = combine_queries(scopus_path, wos_path if wos_path else None)
        df_cleaned = clean_data(df_combined)

        if keyword:
            df_filtered = filter_by_keyword(df_cleaned, keyword)

        # Guardar y generar resultados
        save_data(df_filtered, "filtered_results.csv")
        generate_report(df_filtered, "query_report.html")

        self.update_log("Query Optimizer completed.")

    def update_log(self, message):
        """Mostrar logs (debería conectarse a un log compartido)."""
        print(message)
