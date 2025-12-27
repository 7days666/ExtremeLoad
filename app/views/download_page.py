"""IDE下载页面"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QLabel
)
from PySide6.QtCore import Qt, QThread, Signal
from qfluentwidgets import (
    CardWidget, PushButton, ProgressBar,
    TitleLabel, BodyLabel, InfoBar, InfoBarPosition,
    ComboBox
)
import requests
import os


# 下载源配置
DOWNLOAD_SOURCES = {
    "VSCode": {
        "name": "Visual Studio Code",
        "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
        "filename": "VSCodeSetup.exe",
        "icon": "💻"
    },
    "VS2022": {
        "name": "Visual Studio 2022 Community",
        "url": "https://aka.ms/vs/17/release/vs_community.exe",
        "filename": "vs_community.exe",
        "icon": "🔮"
    },
    "Python": {
        "name": "Python 3.12",
        "url": "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe",
        "filename": "python-3.12.4-amd64.exe",
        "icon": "🐍"
    },
    "Node": {
        "name": "Node.js LTS",
        "url": "https://npmmirror.com/mirrors/node/v20.18.0/node-v20.18.0-x64.msi",
        "filename": "node-v20.18.0-x64.msi",
        "icon": "💚"
    }
}


class DownloadThread(QThread):
    """下载线程"""
    progress = Signal(int)
    finished = Signal(bool, str)
    speed = Signal(str)
    
    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_cancelled = False
    
    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        self.finished.emit(False, "下载已取消")
                        return
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        self.progress.emit(percent)
                        
                        # 计算速度
                        speed_mb = len(chunk) / 1024 / 1024
                        self.speed.emit(f"{speed_mb:.2f} MB/s")
            
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True


class DownloadCard(CardWidget):
    """下载卡片"""
    
    def __init__(self, key, info, parent=None):
        super().__init__(parent)
        self.key = key
        self.info = info
        self.download_thread = None
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题行
        title_layout = QHBoxLayout()
        icon_label = QLabel(self.info["icon"])
        icon_label.setStyleSheet("font-size: 32px;")
        title_label = TitleLabel(self.info["name"])
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 下载按钮
        self.download_btn = PushButton("下载")
        self.download_btn.clicked.connect(self._start_download)
        title_layout.addWidget(self.download_btn)
        
        layout.addLayout(title_layout)
        
        # 进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = BodyLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        self.setFixedHeight(120)
    
    def _start_download(self):
        """开始下载"""
        save_path = os.path.join(self.save_dir, self.info["filename"])
        
        self.download_btn.setEnabled(False)
        self.download_btn.setText("下载中...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)
        self.status_label.setText("正在连接...")
        
        self.download_thread = DownloadThread(self.info["url"], save_path)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.speed.connect(self._on_speed)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.start()
    
    def _on_progress(self, value):
        self.progress_bar.setValue(value)
    
    def _on_speed(self, speed):
        self.status_label.setText(f"下载速度: {speed}")
    
    def _on_finished(self, success, message):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("下载")
        
        if success:
            self.status_label.setText(f"✅ 下载完成: {message}")
            InfoBar.success(
                title="下载完成",
                content=f"{self.info['name']} 已保存到 Downloads 文件夹",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000
            )
        else:
            self.status_label.setText(f"❌ 下载失败: {message}")
            self.progress_bar.setVisible(False)


class DownloadPage(QWidget):
    """IDE下载页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("downloadPage")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 页面标题
        title = TitleLabel("📥 IDE 下载区")
        layout.addWidget(title)
        
        desc = BodyLabel("点击下载按钮，自动下载到 Downloads 文件夹")
        layout.addWidget(desc)
        
        # 下载卡片
        for key, info in DOWNLOAD_SOURCES.items():
            card = DownloadCard(key, info, self)
            layout.addWidget(card)
        
        layout.addStretch()
