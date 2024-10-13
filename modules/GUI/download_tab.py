from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QProgressBar, QFileDialog
from modules.download.downloadworker import DownloadWorker

class DownloadTab(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar widgets para Download Papers
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

        # Crear layout principal
        layout = QVBoxLayout()
        layout.addLayout(csvLayout)
        layout.addWidget(self.logArea)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.beginButton)

        self.setLayout(layout)

        # Conectar señales
        self.browseButton.clicked.connect(self.browse_csv)
        self.beginButton.clicked.connect(self.start_downloads)

    def browse_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csvPathLine.setText(file_name)

    def start_downloads(self):
        csv_path = self.csvPathLine.text()
        if not csv_path:
            self.logArea.append("Please provide a valid CSV path.")
            return

        self.logArea.append("Starting downloads...")

        # Iniciar el proceso de descarga con DownloadWorker
        self.worker = DownloadWorker(csv_path, self.config)
        self.worker.log_signal.connect(self.update_log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()

    def update_log(self, message):
        """Actualiza el área de logs en la pestaña."""
        self.logArea.append(message)

    def update_progress(self, progress):
        """Actualiza la barra de progreso con el valor dado."""
        self.progressBar.setValue(progress)
