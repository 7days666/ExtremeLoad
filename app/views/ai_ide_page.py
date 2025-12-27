"""AI IDE下载页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QScrollArea, QFrame
)
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from qfluentwidgets import (
    CardWidget, PushButton, ProgressBar,
    TitleLabel, BodyLabel, InfoBar, InfoBarPosition,
    FluentIcon as FIF, IconWidget, CheckBox, LineEdit,
    PrimaryPushButton, SearchLineEdit
)
import requests
import os
import subprocess
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AI_IDE_SOURCES = {
    "Kiro": {
        "name": "Kiro",
        "desc": "AWS 出品的 AI IDE",
        "url": "https://prod.download.desktop.kiro.dev/releases/stable/win32-x64/signed/0.8.0/kiro-ide-0.8.0-stable-win32-x64.exe",
        "filename": "kiro-ide-0.8.0-stable-win32-x64.exe",
        "website": "https://kiro.dev/downloads/",
        "icon": FIF.IOT
    },
    "Windsurf": {
        "name": "Windsurf",
        "desc": "Codeium 出品的 AI IDE",
        "url": "https://windsurf-stable.codeiumdata.com/win32-x64-user/stable/f5d6162bf21a6caf7ad124c0ddf9cb1089034608/WindsurfUserSetup-x64-1.13.3.exe",
        "filename": "WindsurfUserSetup-x64-1.13.3.exe",
        "website": "https://codeium.com/windsurf",
        "icon": FIF.CLOUD
    },
}

class DownloadThread(QThread):
    progress = pyqtSignal(int, int, int)
    finished = pyqtSignal(bool, str)
    speed = pyqtSignal(str)
    
    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_cancelled = False
    
    def run(self):
        try:
            save_dir = os.path.dirname(self.save_path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(self.url, stream=True, timeout=120, allow_redirects=True, headers=headers, verify=False)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if self._is_cancelled:
                        f.close()
                        if os.path.exists(self.save_path):
                            os.remove(self.save_path)
                        self.finished.emit(False, "下载已取消")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress.emit(int(downloaded * 100 / total_size), downloaded, total_size)
                        self.speed.emit(f"{len(chunk)/1024:.1f} KB/s")
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True


class AIIDECard(CardWidget):
    def __init__(self, key, info, get_save_dir, get_auto_open, parent=None):
        super().__init__(parent)
        self.key = key
        self.info = info
        self.get_save_dir = get_save_dir
        self.get_auto_open = get_auto_open
        self.download_thread = None
        self.current_save_path = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        title_layout = QHBoxLayout()
        icon_widget = IconWidget(self.info["icon"])
        icon_widget.setFixedSize(32, 32)
        name_layout = QVBoxLayout()
        name_layout.setSpacing(2)
        name_layout.addWidget(TitleLabel(self.info["name"]))
        desc = BodyLabel(self.info["desc"])
        desc.setStyleSheet("color: gray;")
        name_layout.addWidget(desc)
        title_layout.addWidget(icon_widget)
        title_layout.addSpacing(10)
        title_layout.addLayout(name_layout, 1)
        website_btn = PushButton("官网")
        website_btn.setFixedWidth(60)
        website_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.info["website"])))
        title_layout.addWidget(website_btn)
        self.download_btn = PrimaryPushButton("下载")
        self.download_btn.setMinimumWidth(80)
        self.download_btn.clicked.connect(self._start_download)
        title_layout.addWidget(self.download_btn)
        self.cancel_btn = PushButton("取消")
        self.cancel_btn.setMinimumWidth(80)
        self.cancel_btn.clicked.connect(self._cancel_download)
        self.cancel_btn.setVisible(False)
        title_layout.addWidget(self.cancel_btn)
        self.install_btn = PushButton("安装")
        self.install_btn.setMinimumWidth(80)
        self.install_btn.clicked.connect(self._run_installer)
        self.install_btn.setVisible(False)
        title_layout.addWidget(self.install_btn)
        layout.addLayout(title_layout)
        progress_layout = QHBoxLayout()
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar, 1)
        self.size_label = BodyLabel("")
        self.size_label.setVisible(False)
        self.size_label.setFixedWidth(150)
        progress_layout.addWidget(self.size_label)
        layout.addLayout(progress_layout)
        self.status_label = BodyLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        self.setFixedHeight(130)
    
    def _start_download(self):
        save_dir = self.get_save_dir()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.current_save_path = os.path.join(save_dir, self.info["filename"])
        self.download_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.size_label.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("正在连接...")
        self.download_thread = DownloadThread(self.info["url"], self.current_save_path)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.speed.connect(self._on_speed)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.start()
    
    def _cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()
    
    def _on_progress(self, percent, downloaded, total):
        self.progress_bar.setValue(percent)
        self.size_label.setText(f"{downloaded/1024/1024:.1f} MB / {total/1024/1024:.1f} MB")
    
    def _on_speed(self, speed):
        self.status_label.setText(f"下载速度: {speed}")
    
    def _on_finished(self, success, message):
        self.download_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        if success:
            self.status_label.setText("下载完成")
            self.install_btn.setVisible(True)
            InfoBar.success(title="下载完成", content=f"{self.info['name']} 已保存", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
            if self.get_auto_open():
                subprocess.Popen(f'explorer "{os.path.dirname(message)}"')
        else:
            self.status_label.setText(f"失败: {message}")
            self.progress_bar.setVisible(False)
            self.size_label.setVisible(False)
    
    def _run_installer(self):
        if self.current_save_path and os.path.exists(self.current_save_path):
            subprocess.Popen(f'"{self.current_save_path}"', shell=True)


class AIIDEPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("aiIdePage")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads", "AI-IDE")
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
        title_layout.addWidget(IconWidget(FIF.ROBOT))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("AI IDE 下载区"))
        title_layout.addStretch()
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_cards)
        title_layout.addWidget(self.search_edit)
        content_layout.addLayout(title_layout)
        content_layout.addWidget(BodyLabel("如下载失败请点击官网按钮手动下载"))
        settings_card = CardWidget()
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 15, 20, 15)
        path_layout = QHBoxLayout()
        path_layout.addWidget(BodyLabel("保存位置:"))
        self.path_edit = LineEdit()
        self.path_edit.setText(self.save_dir)
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit, 1)
        browse_btn = PushButton("浏览")
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)
        open_btn = PushButton("打开目录")
        open_btn.clicked.connect(self._open_folder)
        path_layout.addWidget(open_btn)
        settings_layout.addLayout(path_layout)
        self.auto_open_checkbox = CheckBox("下载完成后自动打开目录")
        self.auto_open_checkbox.setChecked(True)
        settings_layout.addWidget(self.auto_open_checkbox)
        content_layout.addWidget(settings_card)
        self.cards = []
        for key, info in AI_IDE_SOURCES.items():
            card = AIIDECard(key, info, self._get_save_dir, self._get_auto_open, self)
            self.cards.append(card)
            content_layout.addWidget(card)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _get_save_dir(self):
        return self.path_edit.text()
    
    def _get_auto_open(self):
        return self.auto_open_checkbox.isChecked()
    
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择目录", self.save_dir)
        if folder:
            self.path_edit.setText(folder)
    
    def _open_folder(self):
        folder = self.path_edit.text()
        if not os.path.exists(folder):
            os.makedirs(folder)
        subprocess.Popen(f'explorer "{folder}"')
    
    def _filter_cards(self, text):
        text = text.lower().strip()
        for card in self.cards:
            card.setVisible(not text or text in card.info["name"].lower())
