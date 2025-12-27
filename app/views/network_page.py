"""网络工具页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import QThread, pyqtSignal
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, TextEdit
)
import subprocess
import socket
import requests
import time


class PingThread(QThread):
    """Ping 线程"""
    output = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, host, count=4):
        super().__init__()
        self.host = host
        self.count = count
    
    def run(self):
        try:
            result = subprocess.run(
                f"ping -n {self.count} {self.host}",
                shell=True, capture_output=True, text=True, timeout=30
            )
            self.output.emit(result.stdout or result.stderr)
        except Exception as e:
            self.output.emit(f"错误: {e}")
        self.finished.emit()


class TracertThread(QThread):
    """Traceroute 线程"""
    output = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, host):
        super().__init__()
        self.host = host
    
    def run(self):
        try:
            result = subprocess.run(
                f"tracert -d -h 15 {self.host}",
                shell=True, capture_output=True, text=True, timeout=60
            )
            self.output.emit(result.stdout or result.stderr)
        except Exception as e:
            self.output.emit(f"错误: {e}")
        self.finished.emit()


class SpeedTestThread(QThread):
    """测速线程"""
    output = pyqtSignal(str)
    finished = pyqtSignal(str)
    
    def run(self):
        test_urls = [
            ("阿里云", "https://mirrors.aliyun.com/ubuntu/ls-lR.gz"),
            ("腾讯云", "https://mirrors.cloud.tencent.com/ubuntu/ls-lR.gz"),
            ("清华源", "https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ls-lR.gz"),
        ]
        
        results = []
        for name, url in test_urls:
            self.output.emit(f"测试 {name}...")
            try:
                start = time.time()
                resp = requests.get(url, stream=True, timeout=10)
                downloaded = 0
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    downloaded += len(chunk)
                    if downloaded >= 5*1024*1024:  # 下载 5MB
                        break
                elapsed = time.time() - start
                speed = downloaded / elapsed / 1024 / 1024
                results.append(f"{name}: {speed:.2f} MB/s")
            except Exception as e:
                results.append(f"{name}: 失败 ({e})")
        
        self.finished.emit("\n".join(results))


class NetworkPage(QWidget):
    """网络工具页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("networkPage")
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
        title_layout.addWidget(IconWidget(FIF.WIFI))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("网络工具"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        # IP 信息
        ip_card = CardWidget()
        ip_layout = QVBoxLayout(ip_card)
        ip_layout.setContentsMargins(20, 15, 20, 15)
        ip_layout.addWidget(TitleLabel("IP 信息"))
        
        ip_btn_layout = QHBoxLayout()
        self.local_ip_label = BodyLabel("本机 IP: 点击获取")
        ip_btn_layout.addWidget(self.local_ip_label)
        ip_btn_layout.addStretch()
        
        get_ip_btn = PushButton("获取本机 IP")
        get_ip_btn.clicked.connect(self._get_local_ip)
        ip_btn_layout.addWidget(get_ip_btn)
        
        get_public_btn = PushButton("获取公网 IP")
        get_public_btn.clicked.connect(self._get_public_ip)
        ip_btn_layout.addWidget(get_public_btn)
        ip_layout.addLayout(ip_btn_layout)
        
        self.public_ip_label = BodyLabel("公网 IP: 点击获取")
        ip_layout.addWidget(self.public_ip_label)
        content_layout.addWidget(ip_card)

        # Ping
        ping_card = CardWidget()
        ping_layout = QVBoxLayout(ping_card)
        ping_layout.setContentsMargins(20, 15, 20, 15)
        ping_layout.addWidget(TitleLabel("Ping 测试"))
        
        ping_input_layout = QHBoxLayout()
        self.ping_host = LineEdit()
        self.ping_host.setPlaceholderText("输入域名或 IP，如 baidu.com")
        ping_input_layout.addWidget(self.ping_host, 1)
        
        self.ping_btn = PrimaryPushButton("Ping")
        self.ping_btn.clicked.connect(self._ping)
        ping_input_layout.addWidget(self.ping_btn)
        
        self.tracert_btn = PushButton("Traceroute")
        self.tracert_btn.clicked.connect(self._tracert)
        ping_input_layout.addWidget(self.tracert_btn)
        ping_layout.addLayout(ping_input_layout)
        
        self.ping_output = TextEdit()
        self.ping_output.setReadOnly(True)
        self.ping_output.setMaximumHeight(200)
        ping_layout.addWidget(self.ping_output)
        content_layout.addWidget(ping_card)
        
        # DNS 查询
        dns_card = CardWidget()
        dns_layout = QVBoxLayout(dns_card)
        dns_layout.setContentsMargins(20, 15, 20, 15)
        dns_layout.addWidget(TitleLabel("DNS 查询"))
        
        dns_input_layout = QHBoxLayout()
        self.dns_host = LineEdit()
        self.dns_host.setPlaceholderText("输入域名，如 google.com")
        dns_input_layout.addWidget(self.dns_host, 1)
        
        dns_btn = PrimaryPushButton("查询")
        dns_btn.clicked.connect(self._dns_lookup)
        dns_input_layout.addWidget(dns_btn)
        dns_layout.addLayout(dns_input_layout)
        
        self.dns_result = BodyLabel("")
        dns_layout.addWidget(self.dns_result)
        content_layout.addWidget(dns_card)
        
        # 网络测速
        speed_card = CardWidget()
        speed_layout = QVBoxLayout(speed_card)
        speed_layout.setContentsMargins(20, 15, 20, 15)
        speed_layout.addWidget(TitleLabel("网络测速"))
        speed_layout.addWidget(BodyLabel("测试到国内镜像源的下载速度"))
        
        speed_btn_layout = QHBoxLayout()
        self.speed_btn = PrimaryPushButton("开始测速")
        self.speed_btn.clicked.connect(self._speed_test)
        speed_btn_layout.addWidget(self.speed_btn)
        speed_btn_layout.addStretch()
        speed_layout.addLayout(speed_btn_layout)
        
        self.speed_result = BodyLabel("")
        speed_layout.addWidget(self.speed_result)
        content_layout.addWidget(speed_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    
    def _get_local_ip(self):
        """获取本机 IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.local_ip_label.setText(f"本机 IP: {ip}")
        except Exception as e:
            self.local_ip_label.setText(f"获取失败: {e}")
    
    def _get_public_ip(self):
        """获取公网 IP"""
        try:
            resp = requests.get("https://api.ipify.org?format=json", timeout=5)
            ip = resp.json().get("ip", "未知")
            self.public_ip_label.setText(f"公网 IP: {ip}")
        except Exception as e:
            self.public_ip_label.setText(f"获取失败: {e}")
    
    def _ping(self):
        """Ping 测试"""
        host = self.ping_host.text().strip()
        if not host:
            InfoBar.warning("提示", "请输入域名或 IP", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        self.ping_btn.setEnabled(False)
        self.ping_output.setPlainText("正在 Ping...")
        
        self.ping_thread = PingThread(host)
        self.ping_thread.output.connect(self.ping_output.setPlainText)
        self.ping_thread.finished.connect(lambda: self.ping_btn.setEnabled(True))
        self.ping_thread.start()
    
    def _tracert(self):
        """Traceroute"""
        host = self.ping_host.text().strip()
        if not host:
            InfoBar.warning("提示", "请输入域名或 IP", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        self.tracert_btn.setEnabled(False)
        self.ping_output.setPlainText("正在追踪路由，请稍候...")
        
        self.tracert_thread = TracertThread(host)
        self.tracert_thread.output.connect(self.ping_output.setPlainText)
        self.tracert_thread.finished.connect(lambda: self.tracert_btn.setEnabled(True))
        self.tracert_thread.start()
    
    def _dns_lookup(self):
        """DNS 查询"""
        host = self.dns_host.text().strip()
        if not host:
            return
        
        try:
            ips = socket.gethostbyname_ex(host)
            result = f"域名: {ips[0]}\nIP: {', '.join(ips[2])}"
            self.dns_result.setText(result)
        except Exception as e:
            self.dns_result.setText(f"查询失败: {e}")
    
    def _speed_test(self):
        """网络测速"""
        self.speed_btn.setEnabled(False)
        self.speed_result.setText("正在测速...")
        
        self.speed_thread = SpeedTestThread()
        self.speed_thread.output.connect(lambda msg: self.speed_result.setText(msg))
        self.speed_thread.finished.connect(self._on_speed_finished)
        self.speed_thread.start()
    
    def _on_speed_finished(self, result):
        self.speed_btn.setEnabled(True)
        self.speed_result.setText(result)
