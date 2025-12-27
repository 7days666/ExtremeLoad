"""系统信息页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, IconWidget
)
import os
import subprocess
import platform


class InfoCard(CardWidget):
    """信息卡片"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)
        self.layout.setSpacing(8)
        self.title_label = TitleLabel(title)
        self.layout.addWidget(self.title_label)
        self.grid = QGridLayout()
        self.grid.setSpacing(8)
        self.layout.addLayout(self.grid)
        self.row = 0
    
    def add_item(self, label, value, color=None):
        label_widget = BodyLabel(label)
        label_widget.setStyleSheet("color: gray;")
        value_widget = BodyLabel(str(value))
        if color:
            value_widget.setStyleSheet(f"color: {color};")
        self.grid.addWidget(label_widget, self.row, 0)
        self.grid.addWidget(value_widget, self.row, 1)
        self.row += 1


def get_version(cmd):
    """获取软件版本"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            output = result.stdout.strip() or result.stderr.strip()
            return output.split('\n')[0] if output else "未安装"
        return "未安装"
    except:
        return "未安装"


def get_env_var(name):
    """获取环境变量"""
    value = os.environ.get(name, "")
    return value if value else "未配置"


class SysInfoPage(QWidget):
    """系统信息页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sysInfoPage")
        self._init_ui()
    
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
        title_layout.addWidget(IconWidget(FIF.INFO))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("系统信息"))
        title_layout.addStretch()
        refresh_btn = PushButton("刷新")
        refresh_btn.clicked.connect(self._refresh)
        title_layout.addWidget(refresh_btn)
        content_layout.addLayout(title_layout)
        
        # 系统信息卡片
        self.sys_card = InfoCard("操作系统", self)
        content_layout.addWidget(self.sys_card)
        
        # 开发环境卡片
        self.dev_card = InfoCard("开发环境版本", self)
        content_layout.addWidget(self.dev_card)
        
        # 环境变量卡片
        self.env_card = InfoCard("环境变量", self)
        content_layout.addWidget(self.env_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self._load_info()

    
    def _load_info(self):
        """加载系统信息"""
        # 系统信息
        self.sys_card.add_item("系统:", f"{platform.system()} {platform.release()}")
        self.sys_card.add_item("版本:", platform.version())
        self.sys_card.add_item("架构:", platform.machine())
        self.sys_card.add_item("处理器:", platform.processor()[:50] if platform.processor() else "未知")
        self.sys_card.add_item("计算机名:", platform.node())
        
        # 开发环境版本
        dev_tools = [
            ("Python", "python --version"),
            ("Node.js", "node --version"),
            ("npm", "npm --version"),
            ("Git", "git --version"),
            ("Java", "java -version"),
            ("Go", "go version"),
            ("Rust", "rustc --version"),
            ("Docker", "docker --version"),
        ]
        for name, cmd in dev_tools:
            version = get_version(cmd)
            color = "#4CAF50" if version != "未安装" else "#FF9800"
            self.dev_card.add_item(f"{name}:", version, color)
        
        # 环境变量
        env_vars = ["JAVA_HOME", "GOROOT", "GOPATH", "PYTHON_HOME", "NODE_HOME", "MAVEN_HOME", "PATH"]
        for var in env_vars:
            value = get_env_var(var)
            if var == "PATH":
                value = value[:80] + "..." if len(value) > 80 else value
            color = "#4CAF50" if value != "未配置" else "#FF9800"
            self.dev_card.add_item(f"{var}:", value[:60] + "..." if len(value) > 60 else value, color)
    
    def _refresh(self):
        """刷新信息"""
        # 清空并重新加载
        for card in [self.sys_card, self.dev_card, self.env_card]:
            while card.grid.count():
                item = card.grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            card.row = 0
        self._load_info()
        InfoBar.success("刷新完成", "系统信息已更新", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
