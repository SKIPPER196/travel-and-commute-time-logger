import sys
import os
from PyQt6.QtWidgets import QApplication
from shell.main_window import MainWindow

sys.path.append(os.path.join(os.path.dirname(__file__)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())