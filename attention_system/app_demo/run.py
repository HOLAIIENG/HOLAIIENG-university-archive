import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow
if __name__ == "__main__":
    app = QApplication(sys.argv)
#启动案例主窗口
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
