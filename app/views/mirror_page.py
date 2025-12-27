"""镜像源切换页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, ComboBox, PrimaryPushButton
)
import os
import subprocess


MIRROR_SOURCES = {
    "npm": {
        "name": "npm / yarn",
        "icon": FIF.APPLICATION,
        "mirrors": {
            "官方源": "https://registry.npmjs.org/",
            "淘宝源": "https://registry.npmmirror.com/",
            "腾讯源": "https://mirrors.cloud.tencent.com/npm/",
            "华为源": "https://repo.huaweicloud.com/repository/npm/",
        },
        "get_cmd": "npm config get registry",
        "set_cmd": "npm config set registry {url}",
    },
    "pip": {
        "name": "pip (Python)",
        "icon": FIF.COMMAND_PROMPT,
        "mirrors": {
            "官方源": "https://pypi.org/simple/",
            "清华源": "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "阿里源": "https://mirrors.aliyun.com/pypi/simple/",
            "腾讯源": "https://mirrors.cloud.tencent.com/pypi/simple/",
            "华为源": "https://repo.huaweicloud.com/repository/pypi/simple/",
        },
        "get_cmd": "pip config get global.index-url",
        "set_cmd": "pip config set global.index-url {url}",
    },
    "maven": {
        "name": "Maven",
        "icon": FIF.BOOK_SHELF,
        "mirrors": {
            "官方源": "https://repo.maven.apache.org/maven2/",
            "阿里源": "https://maven.aliyun.com/repository/public/",
            "华为源": "https://repo.huaweicloud.com/repository/maven/",
        },
        "config_file": os.path.join(os.path.expanduser("~"), ".m2", "settings.xml"),
    },
    "go": {
        "name": "Go Proxy",
        "icon": FIF.SPEED_HIGH,
        "mirrors": {
            "官方源": "https://proxy.golang.org,direct",
            "七牛源": "https://goproxy.cn,direct",
            "阿里源": "https://mirrors.aliyun.com/goproxy/,direct",
        },
        "get_cmd": "go env GOPROXY",
        "set_cmd": "go env -w GOPROXY={url}",
    },
}


class MirrorCard(CardWidget):
    """镜像源配置卡片"""
    
    def __init__(self, key, info, parent=None):
        super().__init__(parent)
        self.key = key
        self.info = info
        self._init_ui()
        self._detect_current()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # 标题行
        title_layout = QHBoxLayout()
        icon = IconWidget(self.info["icon"])
        icon.setFixedSize(28, 28)
        title_layout.addWidget(icon)
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel(self.info["name"]))
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 当前源显示
        current_layout = QHBoxLayout()
        current_layout.addWidget(BodyLabel("当前源:"))
        self.current_label = BodyLabel("检测中...")
        self.current_label.setStyleSheet("color: gray;")
        current_layout.addWidget(self.current_label, 1)
        layout.addLayout(current_layout)
        
        # 镜像选择
        select_layout = QHBoxLayout()
        select_layout.addWidget(BodyLabel("切换到:"))
        self.mirror_combo = ComboBox()
        self.mirror_combo.addItems(list(self.info["mirrors"].keys()))
        self.mirror_combo.setMinimumWidth(150)
        select_layout.addWidget(self.mirror_combo)
        
        self.apply_btn = PrimaryPushButton("应用")
        self.apply_btn.clicked.connect(self._apply_mirror)
        select_layout.addWidget(self.apply_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        self.setFixedHeight(140)
    
    def _detect_current(self):
        """检测当前镜像源"""
        if "get_cmd" in self.info:
            try:
                result = subprocess.run(self.info["get_cmd"], shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    current = result.stdout.strip()
                    self.current_label.setText(current if current else "未配置")
                    # 匹配已知镜像
                    for name, url in self.info["mirrors"].items():
                        if url in current or current in url:
                            self.mirror_combo.setCurrentText(name)
                            break
                else:
                    self.current_label.setText("未安装或未配置")
            except:
                self.current_label.setText("检测失败")
        elif "config_file" in self.info:
            if os.path.exists(self.info["config_file"]):
                self.current_label.setText("已有配置文件")
            else:
                self.current_label.setText("未配置")
    
    def _apply_mirror(self):
        """应用镜像源"""
        selected = self.mirror_combo.currentText()
        url = self.info["mirrors"][selected]
        
        if "set_cmd" in self.info:
            try:
                cmd = self.info["set_cmd"].format(url=url)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.current_label.setText(url)
                    InfoBar.success("切换成功", f"{self.info['name']} 已切换到 {selected}", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
                else:
                    InfoBar.error("切换失败", result.stderr or "未知错误", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
            except Exception as e:
                InfoBar.error("切换失败", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        elif "config_file" in self.info:
            self._write_maven_config(url, selected)
    
    def _write_maven_config(self, url, name):
        """写入 Maven 配置"""
        config_dir = os.path.dirname(self.info["config_file"])
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
          http://maven.apache.org/xsd/settings-1.0.0.xsd">
    <mirrors>
        <mirror>
            <id>{name.replace("源", "")}</id>
            <mirrorOf>central</mirrorOf>
            <name>{name}</name>
            <url>{url}</url>
        </mirror>
    </mirrors>
</settings>
'''
        try:
            with open(self.info["config_file"], 'w', encoding='utf-8') as f:
                f.write(xml_content)
            self.current_label.setText(url)
            InfoBar.success("配置成功", f"Maven 配置已写入 {self.info['config_file']}", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        except Exception as e:
            InfoBar.error("配置失败", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)


class MirrorPage(QWidget):
    """镜像源切换页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mirrorPage")
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
        title_layout.addWidget(IconWidget(FIF.SYNC))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("镜像源切换"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        content_layout.addWidget(BodyLabel("一键切换国内镜像源，加速包下载"))
        
        # 镜像源卡片
        for key, info in MIRROR_SOURCES.items():
            card = MirrorCard(key, info, self)
            content_layout.addWidget(card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
