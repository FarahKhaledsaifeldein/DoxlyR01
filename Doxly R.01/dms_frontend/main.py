import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    """Main entry point for the Doxly application."""
    app = QApplication(sys.argv)
    
    # Start with login window
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
