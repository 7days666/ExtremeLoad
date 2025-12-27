"""逆向工具下载页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from qfluentwidgets import (
    CardWidget, PushButton, ProgressBar, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, IconWidget, 
    CheckBox, LineEdit, PrimaryPushButton, SearchLineEdit
)
import requests
import os
import subprocess
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REVERSE_TOOLS = {
    "CheatEngine": {
        "name": "Cheat Engine",
        "desc": "内存扫描修改工具",
        "url": "https://github.com/cheat-engine/cheat-engine/releases/download/7.5/CheatEngine75.exe",
        "filename": "CheatEngine75.exe",
        "website": "https://www.cheatengine.org/",
        "icon": FIF.GAME
    },
    "x64dbg": {
        "name": "x64dbg",
        "desc": "开源 x64/x32 调试器",
        "url": "https://github.com/x64dbg/x64dbg/releases/download/snapshot/snapshot_2024-03-31_12-51.zip",
        "filename": "x64dbg_snapshot.zip",
        "website": "https://x64dbg.com/",
        "icon": FIF.COMMAND_PROMPT
    },
    "Ghidra": {
        "name": "Ghidra",
        "desc": "NSA 开源逆向工程框架",
        "url": "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.1.2_build/ghidra_11.1.2_PUBLIC_20240709.zip",
        "filename": "ghidra_11.1.2_PUBLIC.zip",
        "website": "https://ghidra-sre.org/",
        "icon": FIF.DEVELOPER_TOOLS
    },
    "dnSpy": {
        "name": "dnSpy",
        "desc": ".NET 反编译调试器",
        "url": "https://github.com/dnSpyEx/dnSpy/releases/download/v6.5.1/dnSpy-net-win64.zip",
        "filename": "dnSpy-net-win64.zip",
        "website": "https://github.com/dnSpyEx/dnSpy",
        "icon": FIF.CODE
    },
    "DIE": {
        "name": "Detect It Easy",
        "desc": "查壳/文件类型识别",
        "url": "https://github.com/horsicq/DIE-engine/releases/download/3.09/die_win64_portable_3.09.zip",
        "filename": "die_win64_portable.zip",
        "website": "https://github.com/horsicq/DIE-engine",
        "icon": FIF.SEARCH
    },
    "PEbear": {
        "name": "PE-bear",
        "desc": "PE 文件分析工具",
        "url": "https://github.com/hasherezade/pe-bear/releases/download/v0.6.7.3/PE-bear_0.6.7.3_x64_win.zip",
        "filename": "PE-bear_x64.zip",
        "website": "https://github.com/hasherezade/pe-bear",
        "icon": FIF.DOCUMENT
    },
    "HxD": {
        "name": "HxD",
        "desc": "十六进制编辑器",
        "url": "https://mh-nexus.de/downloads/HxDSetup.zip",
        "filename": "HxDSetup.zip",
        "website": "https://mh-nexus.de/en/hxd/",
        "icon": FIF.EDIT
    },
    "ResourceHacker": {
        "name": "Resource Hacker",
        "desc": "资源编辑器",
        "url": "http://www.angusj.com/resourcehacker/resource_hacker.zip",
        "filename": "resource_hacker.zip",
        "website": "http://www.angusj.com/resourcehacker/",
        "icon": FIF.FOLDER
    },
    "ProcessHacker": {
        "name": "Process Hacker",
        "desc": "进程管理/内存查看",
        "url": "https://github.com/processhacker/processhacker/releases/download/v2.39/processhacker-2.39-bin.zip",
        "filename": "processhacker-bin.zip",
        "website": "https://processhacker.sourceforge.io/",
        "icon": FIF.SPEED_HIGH
    },
    "APIMonitor": {
        "name": "API Monitor",
        "desc": "API 调用监控",
        "url": "http://www.rohitab.com/download/api-monitor-v2r13-x86-x64.zip",
        "filename": "api-monitor.zip",
        "website": "http://www.rohitab.com/apimonitor",
        "icon": FIF.VIEW
    },
}


class DownloadThread(QThread):
    progress = pyqtSignal(int, int, int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_cancelled = False
    
    def run(self):
        try:
            save_dir = os.path.dirname(self.save_path)
            if save_dir and not os.path.exists(save_dir):
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
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True


class ReverseToolCard(CardWidget):
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
        
        self.open_btn = PushButton("打开")
        self.open_btn.setMinimumWidth(80)
        self.open_btn.clicked.connect(self._open_file)
        self.open_btn.setVisible(False)
        title_layout.addWidget(self.open_btn)
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
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.start()
    
    def _cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()
    
    def _on_progress(self, percent, downloaded, total):
        self.progress_bar.setValue(percent)
        self.size_label.setText(f"{downloaded/1024/1024:.1f} MB / {total/1024/1024:.1f} MB")
        self.status_label.setText("下载中...")
    
    def _on_finished(self, success, message):
        self.download_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        if success:
            self.status_label.setText("下载完成")
            self.open_btn.setVisible(True)
            InfoBar.success(title="下载完成", content=f"{self.info['name']} 已保存", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
            if self.get_auto_open():
                subprocess.Popen(f'explorer "{os.path.dirname(message)}"')
        else:
            self.status_label.setText(f"失败: {message}")
            self.progress_bar.setVisible(False)
            self.size_label.setVisible(False)
    
    def _open_file(self):
        if self.current_save_path and os.path.exists(self.current_save_path):
            subprocess.Popen(f'explorer /select,"{self.current_save_path}"')


class ReversePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("reversePage")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads", "ReverseTools")
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
        title_layout.addWidget(IconWidget(FIF.DEVELOPER_TOOLS))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("逆向工具下载"))
        title_layout.addStretch()
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_cards)
        title_layout.addWidget(self.search_edit)
        content_layout.addLayout(title_layout)
        
        content_layout.addWidget(BodyLabel("免费开源的逆向工程工具集"))
        
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
        for key, info in REVERSE_TOOLS.items():
            card = ReverseToolCard(key, info, self._get_save_dir, self._get_auto_open, self)
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
        from PyQt5.QtWidgets import QFileDialog
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
            card.setVisible(not text or text in card.info["name"].lower() or text in card.info["desc"].lower())
