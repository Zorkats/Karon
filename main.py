import sys
from PyQt6.QtWidgets import QApplication
from modules.GUI.mainwindow import MainWindow

# Función principal para ejecutar la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()  # Inicializar la ventana principal de la GUI
    window.show()  # Mostrar la ventana principal
    sys.exit(app.exec())  # Ejecutar el ciclo de eventos de la aplicación