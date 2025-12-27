"""主窗口"""
from PyQt5.QtWidgets import QDesktopWidget
from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF
from .download_page import DownloadPage
from .runtime_page import RuntimePage
from .ai_ide_page import AIIDEPage
from .tools_page import ToolsPage
from .env_config_page import EnvConfigPage
from .mirror_page import MirrorPage
from .sysinfo_page import SysInfoPage
from .settings_page import SettingsPage


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
        self.addSubInterface(self.download_page, FIF.DOWNLOAD, "IDE 下载区")
        
        # AI IDE下载页
        self.ai_ide_page = AIIDEPage(self)
        self.addSubInterface(self.ai_ide_page, FIF.ROBOT, "AI IDE 下载")
        
        # 常用工具下载页
        self.tools_page = ToolsPage(self)
        self.addSubInterface(self.tools_page, FIF.APPLICATION, "常用工具")
        
        # 运行库下载页
        self.runtime_page = RuntimePage(self)
        self.addSubInterface(self.runtime_page, FIF.LIBRARY, "运行库下载")

        # 环境配置页
        self.env_config_page = EnvConfigPage(self)
        self.addSubInterface(self.env_config_page, FIF.DEVELOPER_TOOLS, "环境配置")
        
        # 镜像源切换页
        self.mirror_page = MirrorPage(self)
        self.addSubInterface(self.mirror_page, FIF.SYNC, "镜像源切换")
        
        # 系统信息页
        self.sysinfo_page = SysInfoPage(self)
        self.addSubInterface(self.sysinfo_page, FIF.INFO, "系统信息")
        
        # 设置页（放在底部）
        self.settings_page = SettingsPage(self)
        self.addSubInterface(self.settings_page, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)
    
    def _center_window(self):
        """窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
