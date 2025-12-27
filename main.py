"""
极限负载 / ExtremeLoad
开发者工具箱
"""
import sys
from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme
from app.views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    setTheme(Theme.DARK)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
