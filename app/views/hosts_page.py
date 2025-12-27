"""Hosts 编辑器页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, TextEdit
)
import os
import subprocess
import ctypes


HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"

# 常用 hosts 预设
HOSTS_PRESETS = {
    "GitHub 加速": [
        ("140.82.114.4", "github.com"),
        ("185.199.108.154", "github.githubassets.com"),
        ("185.199.108.133", "raw.githubusercontent.com"),
    ],
    "Google 翻译": [
        ("142.250.4.90", "translate.google.com"),
        ("142.250.4.90", "translate.googleapis.com"),
    ],
}


def is_admin():
    """检查是否有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def read_hosts():
    """读取 hosts 文件"""
    try:
        with open(HOSTS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(HOSTS_PATH, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            return f"# 读取失败: {e}"


def write_hosts(content):
    """写入 hosts 文件"""
    try:
        with open(HOSTS_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "保存成功"
    except PermissionError:
        return False, "需要管理员权限，请以管理员身份运行程序"
    except Exception as e:
        return False, str(e)


def parse_hosts(content):
    """解析 hosts 内容为列表"""
    entries = []
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            ip = parts[0]
            for host in parts[1:]:
                if not host.startswith('#'):
                    entries.append((ip, host))
    return entries


class HostsPage(QWidget):
    """Hosts 编辑器页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hostsPage")
        self._init_ui()
        self._load_hosts()
    
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
        title_layout.addWidget(IconWidget(FIF.GLOBE))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("Hosts 编辑器"))
        title_layout.addStretch()
        
        # 管理员权限提示
        if not is_admin():
            admin_label = BodyLabel("⚠ 需要管理员权限才能保存")
            admin_label.setStyleSheet("color: #FF9800;")
            title_layout.addWidget(admin_label)
        
        content_layout.addLayout(title_layout)

        # 快捷操作
        quick_card = CardWidget()
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(20, 15, 20, 15)
        quick_layout.addWidget(BodyLabel("快捷添加:"))
        
        btn_layout = QHBoxLayout()
        for name, entries in HOSTS_PRESETS.items():
            btn = PushButton(name)
            btn.clicked.connect(lambda checked, e=entries: self._add_preset(e))
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        quick_layout.addLayout(btn_layout)
        content_layout.addWidget(quick_card)
        
        # 添加条目
        add_card = CardWidget()
        add_layout = QHBoxLayout(add_card)
        add_layout.setContentsMargins(20, 15, 20, 15)
        add_layout.addWidget(BodyLabel("IP:"))
        self.ip_edit = LineEdit()
        self.ip_edit.setPlaceholderText("127.0.0.1")
        self.ip_edit.setFixedWidth(150)
        add_layout.addWidget(self.ip_edit)
        add_layout.addWidget(BodyLabel("域名:"))
        self.host_edit = LineEdit()
        self.host_edit.setPlaceholderText("example.com")
        self.host_edit.setFixedWidth(250)
        add_layout.addWidget(self.host_edit)
        add_btn = PrimaryPushButton("添加")
        add_btn.clicked.connect(self._add_entry)
        add_layout.addWidget(add_btn)
        add_layout.addStretch()
        content_layout.addWidget(add_card)
        
        # 编辑器
        editor_card = CardWidget()
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(20, 15, 20, 15)
        
        editor_title_layout = QHBoxLayout()
        editor_title_layout.addWidget(BodyLabel("Hosts 文件内容:"))
        editor_title_layout.addStretch()
        
        refresh_btn = PushButton("刷新")
        refresh_btn.clicked.connect(self._load_hosts)
        editor_title_layout.addWidget(refresh_btn)
        
        open_btn = PushButton("用记事本打开")
        open_btn.clicked.connect(lambda: subprocess.Popen(f'notepad "{HOSTS_PATH}"'))
        editor_title_layout.addWidget(open_btn)
        
        save_btn = PrimaryPushButton("保存")
        save_btn.clicked.connect(self._save_hosts)
        editor_title_layout.addWidget(save_btn)
        editor_layout.addLayout(editor_title_layout)
        
        self.editor = TextEdit()
        self.editor.setMinimumHeight(400)
        self.editor.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        editor_layout.addWidget(self.editor)
        content_layout.addWidget(editor_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    
    def _load_hosts(self):
        """加载 hosts 文件"""
        content = read_hosts()
        self.editor.setPlainText(content)
    
    def _save_hosts(self):
        """保存 hosts 文件"""
        content = self.editor.toPlainText()
        success, msg = write_hosts(content)
        if success:
            InfoBar.success("保存成功", "Hosts 文件已更新", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            # 刷新 DNS 缓存
            subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
        else:
            InfoBar.error("保存失败", msg, parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _add_entry(self):
        """添加条目"""
        ip = self.ip_edit.text().strip()
        host = self.host_edit.text().strip()
        if not ip or not host:
            InfoBar.warning("提示", "请输入 IP 和域名", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        current = self.editor.toPlainText()
        new_line = f"\n{ip}\t{host}"
        self.editor.setPlainText(current + new_line)
        self.ip_edit.clear()
        self.host_edit.clear()
        InfoBar.info("已添加", f"{ip} -> {host}", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _add_preset(self, entries):
        """添加预设"""
        current = self.editor.toPlainText()
        lines = []
        for ip, host in entries:
            lines.append(f"{ip}\t{host}")
        new_content = current + "\n" + "\n".join(lines)
        self.editor.setPlainText(new_content)
        InfoBar.info("已添加", f"添加了 {len(entries)} 条记录", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
