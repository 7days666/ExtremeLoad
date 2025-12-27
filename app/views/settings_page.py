"""设置页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QSettings
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, ComboBox, SwitchButton, LineEdit, PrimaryPushButton
)
from qfluentwidgets import setTheme, Theme
import os


class SettingsPage(QWidget):
    """设置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.settings = QSettings("ExtremeLoad", "Settings")
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        
        content = QWidget()
        content.setStyleSheet("background:transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.SETTING))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("设置"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)

        # 外观设置
        appearance_card = CardWidget()
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(20, 15, 20, 15)
        appearance_layout.setSpacing(12)
        appearance_layout.addWidget(TitleLabel("外观"))
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(BodyLabel("主题模式:"))
        self.theme_combo = ComboBox()
        self.theme_combo.addItems(["深色", "浅色"])
        self.theme_combo.setMinimumWidth(120)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        content_layout.addWidget(appearance_card)
        
        # 代理设置
        proxy_card = CardWidget()
        proxy_layout = QVBoxLayout(proxy_card)
        proxy_layout.setContentsMargins(20, 15, 20, 15)
        proxy_layout.setSpacing(12)
        proxy_layout.addWidget(TitleLabel("网络代理"))
        
        proxy_enable_layout = QHBoxLayout()
        proxy_enable_layout.addWidget(BodyLabel("启用代理:"))
        self.proxy_switch = SwitchButton()
        self.proxy_switch.checkedChanged.connect(self._on_proxy_toggled)
        proxy_enable_layout.addWidget(self.proxy_switch)
        proxy_enable_layout.addStretch()
        proxy_layout.addLayout(proxy_enable_layout)
        
        proxy_addr_layout = QHBoxLayout()
        proxy_addr_layout.addWidget(BodyLabel("代理地址:"))
        self.proxy_edit = LineEdit()
        self.proxy_edit.setPlaceholderText("http://127.0.0.1:7890")
        self.proxy_edit.setMinimumWidth(250)
        proxy_addr_layout.addWidget(self.proxy_edit)
        proxy_addr_layout.addStretch()
        proxy_layout.addLayout(proxy_addr_layout)
        
        proxy_save_btn = PrimaryPushButton("保存代理设置")
        proxy_save_btn.clicked.connect(self._save_proxy)
        proxy_layout.addWidget(proxy_save_btn)
        content_layout.addWidget(proxy_card)

        # 下载设置
        download_card = CardWidget()
        download_layout = QVBoxLayout(download_card)
        download_layout.setContentsMargins(20, 15, 20, 15)
        download_layout.setSpacing(12)
        download_layout.addWidget(TitleLabel("下载设置"))
        
        default_path_layout = QHBoxLayout()
        default_path_layout.addWidget(BodyLabel("默认下载目录:"))
        self.default_path_edit = LineEdit()
        self.default_path_edit.setText(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.default_path_edit.setMinimumWidth(300)
        default_path_layout.addWidget(self.default_path_edit)
        browse_btn = PushButton("浏览")
        browse_btn.clicked.connect(self._browse_default_path)
        default_path_layout.addWidget(browse_btn)
        default_path_layout.addStretch()
        download_layout.addLayout(default_path_layout)
        content_layout.addWidget(download_card)
        
        # 关于
        about_card = CardWidget()
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(20, 15, 20, 15)
        about_layout.setSpacing(8)
        about_layout.addWidget(TitleLabel("关于"))
        about_layout.addWidget(BodyLabel("极限负载 / ExtremeLoad"))
        about_layout.addWidget(BodyLabel("版本: 1.0.0"))
        about_layout.addWidget(BodyLabel("开发者工具箱，让开发准备工作一键搞定"))
        content_layout.addWidget(about_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _load_settings(self):
        """加载设置"""
        theme = self.settings.value("theme", "深色")
        self.theme_combo.setCurrentText(theme)
        
        proxy_enabled = self.settings.value("proxy_enabled", False, type=bool)
        self.proxy_switch.setChecked(proxy_enabled)
        
        proxy_addr = self.settings.value("proxy_addr", "")
        self.proxy_edit.setText(proxy_addr)
        
        default_path = self.settings.value("default_path", os.path.join(os.path.expanduser("~"), "Downloads"))
        self.default_path_edit.setText(default_path)

    
    def _on_theme_changed(self, text):
        """主题切换"""
        if text == "深色":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        self.settings.setValue("theme", text)
        InfoBar.success("主题已切换", f"已切换到{text}模式", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _on_proxy_toggled(self, checked):
        """代理开关"""
        self.settings.setValue("proxy_enabled", checked)
        if checked:
            proxy = self.proxy_edit.text().strip()
            if proxy:
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy
        else:
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)
    
    def _save_proxy(self):
        """保存代理设置"""
        proxy = self.proxy_edit.text().strip()
        self.settings.setValue("proxy_addr", proxy)
        if self.proxy_switch.isChecked() and proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
        InfoBar.success("保存成功", "代理设置已保存", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _browse_default_path(self):
        """浏览默认下载目录"""
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "选择默认下载目录", self.default_path_edit.text())
        if folder:
            self.default_path_edit.setText(folder)
            self.settings.setValue("default_path", folder)
            InfoBar.success("设置成功", "默认下载目录已更新", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
