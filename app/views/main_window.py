"""主窗口"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt
from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF
from .download_page import DownloadPage


class MainWindow(FluentWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("极限负载 / ExtremeLoad")
        self.resize(1000, 700)
        
        self._init_navigation()
        self._center_window()
    
    def _init_navigation(self):
        """初始化导航"""
        # IDE下载页
        self.download_page = DownloadPage(self)
        self.addSubInterface(
            self.download_page,
            FIF.DOWNLOAD,
            "IDE 下载区"
        )
    
    def _center_window(self):
        """窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
