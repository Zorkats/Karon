import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QHBoxLayout, QProgressBar
from PySide6.QtCore import QThread
from modules.download.query_builder import QueryDownloadWorker
from modules.utils import get_base_dir

class QueryBuilderTab(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager

        # Widgets for creating queries
        self.custom_query_input = QTextEdit(self)
        self.custom_query_input.setPlaceholderText("Enter your pre-built query here (optional)")
        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Enter keywords (comma separated)")
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter title (optional)")
        self.author_input = QLineEdit(self)
        self.author_input.setPlaceholderText("Enter author (optional)")
        self.date_range_input = QLineEdit(self)
        self.date_range_input.setPlaceholderText("Enter date range (e.g., 2018-2023)")
        self.language_input = QLineEdit(self)
        self.language_input.setPlaceholderText("Enter language (optional, e.g., English)")
        self.doctype_input = QLineEdit(self)
        self.doctype_input.setPlaceholderText("Enter document type (optional, e.g., ar)")
        self.api_selection = QComboBox(self)
        self.api_selection.addItem("Scopus")
        self.api_selection.addItem("Web of Science")
        self.query_output = QTextEdit(self)
        self.query_output.setPlaceholderText("The generated query will appear here.")
        self.query_output.setReadOnly(True)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.generate_query_button = QPushButton("Generate Query", self)
        self.download_button = QPushButton("Download Data", self)
        self.download_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.custom_query_input)
        layout.addWidget(self.keyword_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.author_input)
        layout.addWidget(self.date_range_input)
        layout.addWidget(self.language_input)
        layout.addWidget(self.doctype_input)
        layout.addWidget(self.api_selection)
        layout.addWidget(self.query_output)
        layout.addWidget(self.progress_bar)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.generate_query_button)
        buttons_layout.addWidget(self.download_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.generate_query_button.clicked.connect(self.generate_query)
        self.custom_query_input.textChanged.connect(self.toggle_download_button)
        self.download_button.clicked.connect(self.download_data)
        

        

    def generate_query(self):
        keywords = [kw.strip() for kw in self.keyword_input.text().split(',') if kw.strip()]
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        date_range = self.date_range_input.text().strip()
        language = self.language_input.text().strip()
        doctype = self.doctype_input.text().strip()

        query_parts = []
        if keywords:
            query_parts.append(f"TITLE-ABS-KEY({' OR '.join(keywords)})")
        if title:
            query_parts.append(f"TITLE({title})")
        if author:
            query_parts.append(f"AUTHOR({author})")
        if date_range:
            years = date_range.split('-')
            if len(years) == 2:
                query_parts.append(f"PUBYEAR > {years[0]} AND PUBYEAR < {years[1]}")
        if language:
            query_parts.append(f"LIMIT-TO(LANGUAGE, \"{language}\")")
        if doctype:
            query_parts.append(f"LIMIT-TO(DOCTYPE, \"{doctype}\")")

        query = ' AND '.join(query_parts)
        self.query_output.setPlainText(query)
        self.download_button.setEnabled(True)


    def download_data(self):
        # Si el campo de query personalizada está vacío, genera una query nueva
        if self.custom_query_input.toPlainText().strip():
            query = self.custom_query_input.toPlainText().strip()
        else:
            query = self.generate_query()
        
        api_type = self.api_selection.currentText()
        scopus_api_key = self.settings_manager.get_setting('elsevier_api')
        insttoken = self.settings_manager.get_setting('elsevier_insttoken') if api_type == "Scopus" else None
        api_key = self.settings_manager.get_setting('wos_api') if api_type == "Web of Science" else scopus_api_key

        self.worker = QueryDownloadWorker(query, api_key, insttoken, api_type)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.log_signal.connect(self.update_log)
        self.worker.finished.connect(self.save_data)  # Conectar el final del hilo a la función save_data

        self.worker.start()

    def save_data(self):
        """Función para guardar los datos descargados."""
        df = self.worker.result  # Obtener el dataframe resultante del worker
        if df is not None and not df.empty:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv)")
            if filename:
                df.to_csv(filename, index=False)
                self.query_output.append(f"Data saved to {filename}")
        else:
            self.query_output.append("No results found or there was an error during the download.")


    def toggle_download_button(self):
            if self.custom_query_input.toPlainText().strip():
                self.download_button.setEnabled(True)
            else:
                self.download_button.setEnabled(False)

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def update_log(self, message):
        self.query_output.append(message)
