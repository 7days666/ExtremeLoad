"""系统环境配置页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QFileDialog
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton
)
import os
import subprocess
import winreg
import glob


def find_java_home():
    """查找 Java 安装目录"""
    # 1. 先检查 where java
    try:
        result = subprocess.run("where java", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            java_path = result.stdout.strip().split('\n')[0]
            # java.exe 在 bin 目录下，需要返回上两级
            if java_path and os.path.exists(java_path):
                bin_dir = os.path.dirname(java_path)
                java_home = os.path.dirname(bin_dir)
                if os.path.exists(os.path.join(java_home, "bin", "java.exe")):
                    return java_home
    except:
        pass
    
    # 2. 常见安装路径
    search_paths = [
        r"C:\Program Files\Eclipse Adoptium\jdk-*",
        r"C:\Program Files\Java\jdk-*",
        r"C:\Program Files\Java\jdk*",
        r"C:\Program Files\Microsoft\jdk-*",
        r"C:\Program Files\Zulu\zulu-*",
        r"C:\Program Files\BellSoft\LibericaJDK-*",
    ]
    for pattern in search_paths:
        matches = glob.glob(pattern)
        if matches:
            return sorted(matches, reverse=True)[0]  # 返回最新版本
    return None


def find_go_root():
    """查找 Go 安装目录"""
    try:
        result = subprocess.run("where go", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            go_path = result.stdout.strip().split('\n')[0]
            if go_path and os.path.exists(go_path):
                bin_dir = os.path.dirname(go_path)
                go_root = os.path.dirname(bin_dir)
                if os.path.exists(os.path.join(go_root, "bin", "go.exe")):
                    return go_root
    except:
        pass
    
    for path in [r"C:\Go", r"C:\Program Files\Go", r"D:\Go"]:
        if os.path.exists(os.path.join(path, "bin", "go.exe")):
            return path
    return None


def find_python_home():
    """查找 Python 安装目录"""
    try:
        result = subprocess.run("where python", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            python_path = result.stdout.strip().split('\n')[0]
            if python_path and os.path.exists(python_path):
                return os.path.dirname(python_path)
    except:
        pass
    
    local_app = os.environ.get("LOCALAPPDATA", "")
    search_paths = [
        os.path.join(local_app, "Programs", "Python", "Python*"),
        r"C:\Python*",
        r"C:\Program Files\Python*",
    ]
    for pattern in search_paths:
        matches = glob.glob(pattern)
        if matches:
            return sorted(matches, reverse=True)[0]
    return None


def find_node_home():
    """查找 Node.js 安装目录"""
    try:
        result = subprocess.run("where node", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            node_path = result.stdout.strip().split('\n')[0]
            if node_path and os.path.exists(node_path):
                return os.path.dirname(node_path)
    except:
        pass
    
    for path in [r"C:\Program Files\nodejs", r"C:\nodejs"]:
        if os.path.exists(os.path.join(path, "node.exe")):
            return path
    return None


def find_maven_home():
    """查找 Maven 安装目录"""
    try:
        result = subprocess.run("where mvn", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            mvn_path = result.stdout.strip().split('\n')[0]
            if mvn_path and os.path.exists(mvn_path):
                bin_dir = os.path.dirname(mvn_path)
                return os.path.dirname(bin_dir)
    except:
        pass
    
    for pattern in [r"C:\apache-maven-*", r"D:\apache-maven-*", r"C:\Program Files\apache-maven-*"]:
        matches = glob.glob(pattern)
        if matches:
            return sorted(matches, reverse=True)[0]
    return None


class EnvVarCard(CardWidget):
    """环境变量配置卡片"""
    
    def __init__(self, name, desc, detect_func, parent=None):
        super().__init__(parent)
        self.name = name
        self.desc = desc
        self.detect_func = detect_func
        self._init_ui()
        self._detect_current()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        title_layout = QHBoxLayout()
        self.title_label = TitleLabel(self.name)
        self.status_label = BodyLabel("")
        self.status_label.setStyleSheet("color: gray;")
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.status_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        desc_label = BodyLabel(self.desc)
        desc_label.setStyleSheet("color: gray;")
        layout.addWidget(desc_label)
        
        path_layout = QHBoxLayout()
        self.path_edit = LineEdit()
        self.path_edit.setPlaceholderText("输入路径或点击自动检测")
        path_layout.addWidget(self.path_edit, 1)
        
        browse_btn = PushButton("浏览")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(browse_btn)
        
        detect_btn = PushButton("自动检测")
        detect_btn.clicked.connect(self._auto_detect)
        path_layout.addWidget(detect_btn)
        
        self.set_btn = PrimaryPushButton("设置")
        self.set_btn.clicked.connect(self._set_env)
        path_layout.addWidget(self.set_btn)
        
        layout.addLayout(path_layout)
        self.setFixedHeight(130)
    
    def _detect_current(self):
        """检测当前环境变量"""
        # 先从注册表读取
        value = self._read_from_registry()
        if not value:
            value = os.environ.get(self.name, "")
        
        if value:
            self.path_edit.setText(value)
            self.status_label.setText("✓ 已配置")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText("未配置")
            self.status_label.setStyleSheet("color: #FF9800;")
    
    def _read_from_registry(self):
        """从注册表读取环境变量"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, self.name)
            winreg.CloseKey(key)
            return value
        except:
            pass
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, self.name)
            winreg.CloseKey(key)
            return value
        except:
            pass
        return None

    
    def _browse(self):
        """浏览选择目录"""
        folder = QFileDialog.getExistingDirectory(self, f"选择 {self.name} 目录", self.path_edit.text() or "C:\\")
        if folder:
            self.path_edit.setText(folder)
    
    def _auto_detect(self):
        """自动检测路径"""
        if self.detect_func:
            path = self.detect_func()
            if path and os.path.exists(path):
                self.path_edit.setText(path)
                InfoBar.success("检测成功", f"找到: {path}", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
                return
        InfoBar.warning("未找到", "请手动选择路径", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _set_env(self):
        """设置环境变量"""
        path = self.path_edit.text().strip()
        if not path:
            InfoBar.warning("提示", "请输入路径", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        if not os.path.exists(path):
            InfoBar.warning("提示", "路径不存在", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, self.name, 0, winreg.REG_EXPAND_SZ, path)
            winreg.CloseKey(key)
            
            # 广播环境变量更改消息
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0, 1000, None)
            
            self.status_label.setText("✓ 已配置")
            self.status_label.setStyleSheet("color: #4CAF50;")
            InfoBar.success("设置成功", f"{self.name} 已设置，新终端生效", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        except Exception as e:
            InfoBar.error("设置失败", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)


class EnvConfigPage(QWidget):
    """系统环境配置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("envConfigPage")
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
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.SETTING))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("系统环境配置"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        content_layout.addWidget(BodyLabel("一键配置开发环境变量，设置后新开终端生效"))
        
        # 环境变量配置
        env_configs = [
            ("JAVA_HOME", "Java 安装目录 (JDK)", find_java_home),
            ("GOROOT", "Go 安装目录", find_go_root),
            ("GOPATH", "Go 工作目录", lambda: os.path.join(os.path.expanduser("~"), "go")),
            ("PYTHON_HOME", "Python 安装目录", find_python_home),
            ("NODE_HOME", "Node.js 安装目录", find_node_home),
            ("MAVEN_HOME", "Maven 安装目录", find_maven_home),
            ("RUSTUP_HOME", "Rust 安装目录", lambda: os.path.join(os.path.expanduser("~"), ".rustup") if os.path.exists(os.path.join(os.path.expanduser("~"), ".rustup")) else None),
            ("CARGO_HOME", "Cargo 目录", lambda: os.path.join(os.path.expanduser("~"), ".cargo") if os.path.exists(os.path.join(os.path.expanduser("~"), ".cargo")) else None),
        ]
        
        for name, desc, detect_func in env_configs:
            card = EnvVarCard(name, desc, detect_func, self)
            content_layout.addWidget(card)
        
        # PATH 提示卡片
        path_card = CardWidget()
        path_layout = QVBoxLayout(path_card)
        path_layout.setContentsMargins(20, 15, 20, 15)
        path_layout.addWidget(TitleLabel("PATH 配置提示"))
        path_layout.addWidget(BodyLabel("设置完成后，建议将以下路径添加到 PATH:"))
        path_layout.addWidget(BodyLabel("  • %JAVA_HOME%\\bin"))
        path_layout.addWidget(BodyLabel("  • %GOROOT%\\bin"))
        path_layout.addWidget(BodyLabel("  • %MAVEN_HOME%\\bin"))
        
        open_env_btn = PushButton("打开系统环境变量设置")
        open_env_btn.clicked.connect(lambda: subprocess.Popen("rundll32 sysdm.cpl,EditEnvironmentVariables"))
        path_layout.addWidget(open_env_btn)
        content_layout.addWidget(path_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
