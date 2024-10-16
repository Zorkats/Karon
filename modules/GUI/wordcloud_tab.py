from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QTextEdit, QHBoxLayout
from wordcloud import WordCloud
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap
import os
from PyPDF2 import PdfReader
from io import BytesIO

class WordCloudWorker(QThread):
    wordcloud_generated = Signal(QPixmap)
    log_signal = Signal(str)
    finished = Signal()

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        try:
            self.log_signal.emit("Starting WordCloud generation...")

            pdf_files = [f for f in os.listdir(self.folder_path) if f.endswith('.pdf')]
            text_content = ""
            total_files = len(pdf_files)

            if total_files == 0:
                self.log_signal.emit("No PDF files found in the selected folder.")
                return

            self.log_signal.emit(f"Found {total_files} PDF files. Extracting text...")

            for index, pdf_file in enumerate(pdf_files):
                try:
                    pdf_path = os.path.join(self.folder_path, pdf_file)
                    self.log_signal.emit(f"Processing {pdf_file} ({index + 1}/{total_files})...")
                    with open(pdf_path, 'rb') as f:
                        reader = PdfReader(f)
                        for page_num, page in enumerate(reader.pages):
                            text = page.extract_text()
                            if text:
                                text_content += text
                                self.log_signal.emit(f"Extracted text from page {page_num + 1} of {pdf_file}")
                            else:
                                self.log_signal.emit(f"Warning: Page {page_num + 1} of {pdf_file} is empty.")
                except Exception as e:
                    self.log_signal.emit(f"Failed to process {pdf_file}: {e}")

            if not text_content:
                self.log_signal.emit("No valid text extracted from the PDFs.")
                return

            self.log_signal.emit("Generating WordCloud...")
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_content)

            image_buffer = BytesIO()
            wordcloud.to_image().save(image_buffer, format='PNG')
            image_data = image_buffer.getvalue()

            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                self.wordcloud_generated.emit(pixmap)
                self.log_signal.emit("WordCloud generation completed.")
            else:
                self.log_signal.emit("Failed to generate WordCloud image.")
        except Exception as e:
            self.log_signal.emit(f"Error: {e}")
        finally:
            self.quit()  # Asegurar que el hilo termine siempre
            self.finished.emit()


class WordCloudTab(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar widgets para WordCloud
        self.stats_folder_input = QLineEdit(self)
        self.stats_folder_input.setPlaceholderText("Select the folder with downloaded papers")
        self.browse_stats_folder_button = QPushButton("Browse", self)
        self.wordcloud_button = QPushButton("Generate WordCloud")
        self.wordcloud_label = QLabel(self)
        self.save_wordcloud_button = QPushButton("Save WordCloud Image")
        self.save_wordcloud_button.setEnabled(False)
        self.logArea = QTextEdit(self)
        self.logArea.setPlaceholderText("Logs will be displayed here.")
        self.logArea.setReadOnly(True)

        # Crear layout principal
        layout = QVBoxLayout()

        stats_csv_layout = QHBoxLayout()
        stats_csv_layout.addWidget(self.stats_folder_input)
        stats_csv_layout.addWidget(self.browse_stats_folder_button)

        layout.addLayout(stats_csv_layout)
        layout.addWidget(self.wordcloud_button)
        layout.addWidget(self.wordcloud_label)
        layout.addWidget(self.save_wordcloud_button)
        layout.addWidget(self.logArea)

        self.setLayout(layout)

        # Conectar señales
        self.browse_stats_folder_button.clicked.connect(self.browse_stats_folder)
        self.wordcloud_button.clicked.connect(self.start_wordcloud_generation)
        self.save_wordcloud_button.clicked.connect(self.save_wordcloud_image)

    def browse_stats_folder(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Select Folder with Downloaded Papers")
        if folder_name:
            self.stats_folder_input.setText(folder_name)

    def start_wordcloud_generation(self):
        stats_folder_path = self.stats_folder_input.text()

        if not stats_folder_path:
            self.update_log("Please provide a valid folder path.")
            return

        self.wordcloud_button.setEnabled(False)  # Desactivar el botón mientras se genera el WordCloud

        # Iniciar el hilo para generar el WordCloud
        self.worker = WordCloudWorker(stats_folder_path)
        self.worker.wordcloud_generated.connect(self.display_wordcloud)
        self.worker.log_signal.connect(self.update_log)
        self.worker.finished.connect(lambda: self.wordcloud_button.setEnabled(True))  # Reactivar el botón cuando termine
        self.worker.start()

    def display_wordcloud(self, pixmap):
        self.wordcloud_label.setPixmap(pixmap)
        self.save_wordcloud_button.setEnabled(True)

    def save_wordcloud_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save WordCloud Image", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            try:
                pixmap = self.wordcloud_label.pixmap()
                if pixmap:
                    pixmap.save(file_name)
                    self.logArea.append(f"WordCloud image saved to {file_name}")
                else:
                    self.logArea.append("No WordCloud image to save.")
            except Exception as e:
                self.logArea.append(f"Failed to save WordCloud image: {e}")

    def update_log(self, message):
        """Actualiza el área de logs en la pestaña."""
        self.logArea.append(message)
