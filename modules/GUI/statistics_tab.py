from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QFileDialog, QHBoxLayout
import os
from PyPDF2 import PdfReader

class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar widgets para Statistics
        self.stats_folder_input = QLineEdit(self)
        self.stats_folder_input.setPlaceholderText("Select the folder with downloaded papers")
        self.browse_stats_folder_button = QPushButton("Browse", self)
        self.show_stats_button = QPushButton("Show Statistics", self)
        self.stats_area = QTextEdit(self)
        self.stats_area.setReadOnly(True)

        # Crear layout principal
        layout = QVBoxLayout()

        stats_csv_layout = QHBoxLayout()
        stats_csv_layout.addWidget(self.stats_folder_input)
        stats_csv_layout.addWidget(self.browse_stats_folder_button)

        layout.addLayout(stats_csv_layout)
        layout.addWidget(self.show_stats_button)
        layout.addWidget(self.stats_area)

        self.setLayout(layout)

        # Conectar señales
        self.browse_stats_folder_button.clicked.connect(self.browse_stats_folder)
        self.show_stats_button.clicked.connect(self.show_statistics)

    def browse_stats_folder(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Select Folder with Downloaded Papers")
        if folder_name:
            self.stats_folder_input.setText(folder_name)

    def show_statistics(self):
        stats_folder_path = self.stats_folder_input.text()

        if not stats_folder_path:
            self.stats_area.append("Please provide a valid folder path.")
            return

        # Obtener todos los archivos PDF de la carpeta
        pdf_files = [f for f in os.listdir(stats_folder_path) if f.endswith('.pdf')]
        total_papers = len(pdf_files)
        total_pages = 0
        failed_files = []

        # Procesar cada archivo PDF y obtener estadísticas
        for pdf_file in pdf_files:
            try:
                pdf_path = os.path.join(stats_folder_path, pdf_file)
                with open(pdf_path, 'rb') as f:
                    reader = PdfReader(f)
                    num_pages = len(reader.pages)
                    total_pages += num_pages
            except Exception as e:
                failed_files.append(pdf_file)
                self.stats_area.append(f"Failed to process {pdf_file}: {e}")

        # Calcular las estadísticas finales
        avg_pages = total_pages / total_papers if total_papers > 0 else 0

        # Mostrar las estadísticas en el área de texto
        self.stats_area.clear()
        self.stats_area.append(f"Total Papers: {total_papers}")
        self.stats_area.append(f"Total Pages: {total_pages}")
        self.stats_area.append(f"Average Pages per Paper: {avg_pages:.2f}")
        if failed_files:
            self.stats_area.append(f"Failed to process {len(failed_files)} files.")
            self.stats_area.append("\n".join(failed_files))
