import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Gate Vehicle Monitor")
    
    # Instantiate and display the main window
    window = MainWindow()
    window.show()
    
    # Run the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()