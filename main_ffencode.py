import sys

from PySide6.QtWidgets import QApplication

from service.ui_service import MyApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApplication()
    window.show()
    sys.exit(app.exec())
