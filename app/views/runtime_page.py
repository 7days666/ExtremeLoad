"""运行库下载页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QFileDialog, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from qfluentwidgets import (
    CardWidget, PushButton, ProgressBar,
    TitleLabel, BodyLabel, InfoBar, InfoBarPosition,
    FluentIcon as FIF, IconWidget, CheckBox, LineEdit,
    PrimaryPushButton, SearchLineEdit
)
import requests
import os
import subprocess


# 运行库下载源配置
RUNTIME_SOURCES = {
    # VC++ 运行库
    "vcredist15-22_x86": {
        "name": "VC++ 2015-2022 x86",
        "url": "https://aka.ms/vs/17/release/vc_redist.x86.exe",
        "filename": "vc_redist.x86.exe",
        "category": "vcredist"
    },
    "vcredist15-22_x64": {
        "name": "VC++ 2015-2022 x64",
        "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
        "filename": "vc_redist.x64.exe",
        "category": "vcredist"
    },
    "vcredist_2013_x86": {
        "name": "VC++ 2013 x86",
        "url": "https://aka.ms/highdpimfc2013x86enu",
        "filename": "vcredist_2013_x86.exe",
        "category": "vcredist"
    },
    "vcredist_2013_x64": {
        "name": "VC++ 2013 x64",
        "url": "https://aka.ms/highdpimfc2013x64enu",
        "filename": "vcredist_2013_x64.exe",
        "category": "vcredist"
    },
    "vcredist_2012_x86": {
        "name": "VC++ 2012 x86",
        "url": "https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x86.exe",
        "filename": "vcredist_2012_x86.exe",
        "category": "vcredist"
    },
    "vcredist_2012_x64": {
        "name": "VC++ 2012 x64",
        "url": "https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe",
        "filename": "vcredist_2012_x64.exe",
        "category": "vcredist"
    },
    "vcredist_2010_x86": {
        "name": "VC++ 2010 x86",
        "url": "https://download.microsoft.com/download/1/6/5/165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x86.exe",
        "filename": "vcredist_2010_x86.exe",
        "category": "vcredist"
    },
    "vcredist_2010_x64": {
        "name": "VC++ 2010 x64",
        "url": "https://download.microsoft.com/download/1/6/5/165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x64.exe",
        "filename": "vcredist_2010_x64.exe",
        "category": "vcredist"
    },
    "vcredist_2008_x86": {
        "name": "VC++ 2008 x86",
        "url": "https://download.microsoft.com/download/5/D/8/5D8C65CB-C849-4025-8E95-C3966CAFD8AE/vcredist_x86.exe",
        "filename": "vcredist_2008_x86.exe",
        "category": "vcredist"
    },
    "vcredist_2008_x64": {
        "name": "VC++ 2008 x64",
        "url": "https://download.microsoft.com/download/5/D/8/5D8C65CB-C849-4025-8E95-C3966CAFD8AE/vcredist_x64.exe",
        "filename": "vcredist_2008_x64.exe",
        "category": "vcredist"
    },
    "vcredist_2005_x86": {
        "name": "VC++ 2005 x86",
        "url": "https://download.microsoft.com/download/8/B/4/8B42259F-5D70-43F4-AC2E-4B208FD8D66A/vcredist_x86.EXE",
        "filename": "vcredist_2005_x86.exe",
        "category": "vcredist"
    },
    "vcredist_2005_x64": {
        "name": "VC++ 2005 x64",
        "url": "https://download.microsoft.com/download/8/B/4/8B42259F-5D70-43F4-AC2E-4B208FD8D66A/vcredist_x64.EXE",
        "filename": "vcredist_2005_x64.exe",
        "category": "vcredist"
    },
    # .NET Framework
    "dotnet_4.0": {
        "name": ".NET Framework 4.0",
        "url": "https://download.microsoft.com/download/9/5/A/95A9616B-7A37-4AF6-BC36-D6EA96C8DAAE/dotNetFx40_Full_x86_x64.exe",
        "filename": "dotNetFx40_Full_x86_x64.exe",
        "category": "dotnet"
    },
    "dotnet_4.5": {
        "name": ".NET Framework 4.5",
        "url": "https://download.microsoft.com/download/B/A/4/BA4A7E71-2906-4B2D-A0E1-80CF16844F5F/dotNetFx45_Full_setup.exe",
        "filename": "dotNetFx45_Full_setup.exe",
        "category": "dotnet"
    },
    "dotnet_4.8": {
        "name": ".NET Framework 4.8",
        "url": "https://download.visualstudio.microsoft.com/download/pr/2d6bb6b2-226a-4baa-bdec-798822606ff1/8494001c276a4b96804cde7829c04d7f/ndp48-x86-x64-allos-enu.exe",
        "filename": "ndp48-x86-x64-allos-enu.exe",
        "category": "dotnet"
    },
    # msvsmon 远程调试器
    "msvsmon_10_x86": {
        "name": "msvsmon 2010 x86",
        "url": "https://download.microsoft.com/download/A/1/4/A14D0D4D-E2A2-4771-9D66-F8D14E07F247/rtools_setup_x86.exe",
        "filename": "msvsmon_2010_x86.exe",
        "category": "msvsmon"
    },
    "msvsmon_10_x64": {
        "name": "msvsmon 2010 x64",
        "url": "https://download.microsoft.com/download/A/1/4/A14D0D4D-E2A2-4771-9D66-F8D14E07F247/rtools_setup_x64.exe",
        "filename": "msvsmon_2010_x64.exe",
        "category": "msvsmon"
    },
    "msvsmon_15_x86": {
        "name": "msvsmon 2015 x86",
        "url": "https://aka.ms/vs/15/release/RemoteTools.x86ret.enu.exe",
        "filename": "msvsmon_2015_x86.exe",
        "category": "msvsmon"
    },
    "msvsmon_15_x64": {
        "name": "msvsmon 2015 x64",
        "url": "https://aka.ms/vs/15/release/RemoteTools.amd64ret.enu.exe",
        "filename": "msvsmon_2015_x64.exe",
        "category": "msvsmon"
    },
    "msvsmon_19_x86": {
        "name": "msvsmon 2019 x86",
        "url": "https://aka.ms/vs/16/release/RemoteTools.x86ret.enu.exe",
        "filename": "msvsmon_2019_x86.exe",
        "category": "msvsmon"
    },
    "msvsmon_19_x64": {
        "name": "msvsmon 2019 x64",
        "url": "https://aka.ms/vs/16/release/RemoteTools.amd64ret.enu.exe",
        "filename": "msvsmon_2019_x64.exe",
        "category": "msvsmon"
    },
}


class DownloadThread(QThread):
    """下载线程"""
    progress = pyqtSignal(int, int, int)
    finished = pyqtSignal(bool, str)
    
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
                        f.close()
                        if os.path.exists(self.save_path):
                            os.remove(self.save_path)
                        self.finished.emit(False, "下载已取消")
                        return
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        self.progress.emit(percent, downloaded, total_size)
            
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True


class RuntimeButton(CardWidget):
    """运行库下载按钮"""
    
    def __init__(self, key, info, get_save_dir, get_auto_open, parent=None):
        super().__init__(parent)
        self.key = key
        self.info = info
        self.get_save_dir = get_save_dir
        self.get_auto_open = get_auto_open
        self.download_thread = None
        self.current_save_path = None
        
        self._is_downloading = False
        self._is_downloaded = False
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.name_label = BodyLabel(self.info["name"])
        layout.addWidget(self.name_label, 1)
        
        self.btn = PushButton("下载")
        self.btn.setFixedWidth(70)
        self.btn.clicked.connect(self._on_click)
        layout.addWidget(self.btn)
        
        self.setFixedHeight(50)
        self.setMinimumWidth(200)
    
    def _on_click(self):
        if self._is_downloading:
            if self.download_thread:
                self.download_thread.cancel()
        elif self._is_downloaded:
            self._run_installer()
        else:
            self._start_download()
    
    def _start_download(self):
        save_dir = self.get_save_dir()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        save_path = os.path.join(save_dir, self.info["filename"])
        self.current_save_path = save_path
        
        self._is_downloading = True
        self.btn.setText("0%")
        
        self.download_thread = DownloadThread(self.info["url"], save_path)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.start()
    
    def _on_progress(self, percent, downloaded, total):
        self.btn.setText(f"{percent}%")
    
    def _on_finished(self, success, message):
        self._is_downloading = False
        
        if success:
            self._is_downloaded = True
            self.btn.setText("安装")
            
            InfoBar.success(
                title="下载完成",
                content=f"{self.info['name']} 下载完成",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000
            )
            
            # 自动打开目录
            if self.get_auto_open():
                folder = os.path.dirname(self.current_save_path)
                subprocess.Popen(f'explorer "{folder}"')
        else:
            self.btn.setText("下载")
            if "取消" not in message:
                InfoBar.error(
                    title="下载失败",
                    content=message,
                    parent=self.window(),
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000
                )
    
    def _run_installer(self):
        if self.current_save_path and os.path.exists(self.current_save_path):
            subprocess.Popen(f'"{self.current_save_path}"', shell=True)


class RuntimePage(QWidget):
    """运行库下载页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("runtimePage")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Runtimes")
        self.buttons = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # 标题
        title_layout = QHBoxLayout()
        title_icon = IconWidget(FIF.LIBRARY)
        title_icon.setFixedSize(28, 28)
        title = TitleLabel("运行库下载区")
        title_layout.addWidget(title_icon)
        title_layout.addSpacing(8)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # 搜索框
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索运行库...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_buttons)
        title_layout.addWidget(self.search_edit)
        
        content_layout.addLayout(title_layout)
        
        # 设置区域
        settings_card = CardWidget()
        settings_layout = QHBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 15, 20, 15)
        
        path_label = BodyLabel("保存位置:")
        self.path_edit = LineEdit()
        self.path_edit.setText(self.save_dir)
        self.path_edit.setReadOnly(True)
        
        browse_btn = PushButton("浏览")
        browse_btn.clicked.connect(self._browse_folder)
        
        open_btn = PushButton("打开目录")
        open_btn.clicked.connect(self._open_folder)
        
        settings_layout.addWidget(path_label)
        settings_layout.addWidget(self.path_edit, 1)
        settings_layout.addWidget(browse_btn)
        settings_layout.addWidget(open_btn)
        
        content_layout.addWidget(settings_card)
        
        # 自动打开选项
        self.auto_open_checkbox = CheckBox("下载完成后自动打开目录")
        self.auto_open_checkbox.setChecked(True)
        content_layout.addWidget(self.auto_open_checkbox)
        
        # VC++ 运行库
        vc_card = CardWidget()
        vc_layout = QVBoxLayout(vc_card)
        vc_layout.setContentsMargins(20, 15, 20, 15)
        vc_layout.setSpacing(15)
        
        vc_title = BodyLabel("Visual C++ 运行库")
        vc_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        vc_layout.addWidget(vc_title)
        
        vc_grid = QGridLayout()
        vc_grid.setSpacing(10)
        row, col = 0, 0
        for key, info in RUNTIME_SOURCES.items():
            if info["category"] == "vcredist":
                btn = RuntimeButton(key, info, self._get_save_dir, self._get_auto_open, self)
                self.buttons.append(btn)
                vc_grid.addWidget(btn, row, col)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
        vc_layout.addLayout(vc_grid)
        content_layout.addWidget(vc_card)
        
        # .NET Framework
        dotnet_card = CardWidget()
        dotnet_layout = QVBoxLayout(dotnet_card)
        dotnet_layout.setContentsMargins(20, 15, 20, 15)
        dotnet_layout.setSpacing(15)
        
        dotnet_title = BodyLabel(".NET Framework")
        dotnet_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        dotnet_layout.addWidget(dotnet_title)
        
        dotnet_grid = QGridLayout()
        dotnet_grid.setSpacing(10)
        row, col = 0, 0
        for key, info in RUNTIME_SOURCES.items():
            if info["category"] == "dotnet":
                btn = RuntimeButton(key, info, self._get_save_dir, self._get_auto_open, self)
                self.buttons.append(btn)
                dotnet_grid.addWidget(btn, row, col)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
        dotnet_layout.addLayout(dotnet_grid)
        content_layout.addWidget(dotnet_card)
        
        # msvsmon 远程调试器
        msvsmon_card = CardWidget()
        msvsmon_layout = QVBoxLayout(msvsmon_card)
        msvsmon_layout.setContentsMargins(20, 15, 20, 15)
        msvsmon_layout.setSpacing(15)
        
        msvsmon_title = BodyLabel("msvsmon 远程调试器")
        msvsmon_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        msvsmon_layout.addWidget(msvsmon_title)
        
        msvsmon_grid = QGridLayout()
        msvsmon_grid.setSpacing(10)
        row, col = 0, 0
        for key, info in RUNTIME_SOURCES.items():
            if info["category"] == "msvsmon":
                btn = RuntimeButton(key, info, self._get_save_dir, self._get_auto_open, self)
                self.buttons.append(btn)
                msvsmon_grid.addWidget(btn, row, col)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
        msvsmon_layout.addLayout(msvsmon_grid)
        content_layout.addWidget(msvsmon_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _get_save_dir(self):
        return self.path_edit.text()
    
    def _get_auto_open(self):
        return self.auto_open_checkbox.isChecked()
    
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择保存目录", self.save_dir)
        if folder:
            self.path_edit.setText(folder)
    
    def _open_folder(self):
        folder = self.path_edit.text()
        if not os.path.exists(folder):
            os.makedirs(folder)
        subprocess.Popen(f'explorer "{folder}"')
    
    def _filter_buttons(self, text):
        text = text.lower().strip()
        for btn in self.buttons:
            name = btn.info["name"].lower()
            if not text or text in name:
                btn.setVisible(True)
            else:
                btn.setVisible(False)
