"""主窗口"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt
from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF
from .download_page import DownloadPage
from .runtime_page import RuntimePage


class MainWindow(FluentWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("极限负载 / ExtremeLoad")
        self.resize(1200, 800)
        
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
        
        # 运行库下载页
        self.runtime_page = RuntimePage(self)
        self.addSubInterface(
            self.runtime_page,
            FIF.LIBRARY,
            "运行库下载"
        )
    
    def _center_window(self):
        """窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
