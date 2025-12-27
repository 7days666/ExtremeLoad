"""系统清理页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import QThread, pyqtSignal
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, CheckBox, ProgressBar
)
import os
import shutil
import glob


class CleanThread(QThread):
    """清理线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int, int)  # 文件数, 大小(bytes)
    
    def __init__(self, paths):
        super().__init__()
        self.paths = paths
    
    def run(self):
        total_files = 0
        total_size = 0
        
        for path in self.paths:
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        size = os.path.getsize(path)
                        os.remove(path)
                        total_files += 1
                        total_size += size
                        self.progress.emit(f"删除: {path}")
                    elif os.path.isdir(path):
                        for root, dirs, files in os.walk(path):
                            for f in files:
                                try:
                                    fp = os.path.join(root, f)
                                    size = os.path.getsize(fp)
                                    os.remove(fp)
                                    total_files += 1
                                    total_size += size
                                except:
                                    pass
                except:
                    pass
        
        self.finished.emit(total_files, total_size)


def get_folder_size(path):
    """获取文件夹大小"""
    total = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
    except:
        pass
    return total


def format_size(size):
    """格式化大小"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size/1024/1024:.1f} MB"
    else:
        return f"{size/1024/1024/1024:.2f} GB"


# 清理项配置
CLEAN_ITEMS = {
    "temp_user": {
        "name": "用户临时文件",
        "paths": [os.environ.get("TEMP", "")],
        "desc": "用户 Temp 目录"
    },
    "temp_win": {
        "name": "Windows 临时文件",
        "paths": [r"C:\Windows\Temp"],
        "desc": "系统 Temp 目录"
    },
    "prefetch": {
        "name": "预读取文件",
        "paths": [r"C:\Windows\Prefetch"],
        "desc": "程序预读取缓存"
    },
    "recent": {
        "name": "最近文档记录",
        "paths": [os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Recent")],
        "desc": "最近打开的文件记录"
    },
    "thumbnail": {
        "name": "缩略图缓存",
        "paths": [os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Windows\Explorer")],
        "desc": "图片缩略图缓存"
    },
    "log": {
        "name": "系统日志",
        "paths": [r"C:\Windows\Logs"],
        "desc": "Windows 日志文件"
    },
    "update": {
        "name": "Windows 更新缓存",
        "paths": [r"C:\Windows\SoftwareDistribution\Download"],
        "desc": "Windows Update 下载缓存"
    },
}


class CleanItemCard(CardWidget):
    """清理项卡片"""
    def __init__(self, key, info, parent=None):
        super().__init__(parent)
        self.key = key
        self.info = info
        self._init_ui()
        self._scan_size()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        self.checkbox = CheckBox(self.info["name"])
        self.checkbox.setChecked(True)
        layout.addWidget(self.checkbox)
        
        self.desc_label = BodyLabel(self.info["desc"])
        self.desc_label.setStyleSheet("color: gray;")
        layout.addWidget(self.desc_label)
        layout.addStretch()
        
        self.size_label = BodyLabel("计算中...")
        layout.addWidget(self.size_label)
        
        self.setFixedHeight(60)
    
    def _scan_size(self):
        """扫描大小"""
        total = 0
        for path in self.info["paths"]:
            total += get_folder_size(path)
        self.size_label.setText(format_size(total))
        self.size = total
    
    def is_checked(self):
        return self.checkbox.isChecked()
    
    def get_paths(self):
        return self.info["paths"]


class CleanerPage(QWidget):
    """系统清理页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cleanerPage")
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
        title_layout.addWidget(IconWidget(FIF.DELETE))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("系统清理"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        content_layout.addWidget(BodyLabel("清理系统垃圾文件，释放磁盘空间（需要管理员权限）"))

        # 清理项
        self.cards = []
        for key, info in CLEAN_ITEMS.items():
            card = CleanItemCard(key, info, self)
            self.cards.append(card)
            content_layout.addWidget(card)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        scan_btn = PushButton("重新扫描")
        scan_btn.clicked.connect(self._scan_all)
        btn_layout.addWidget(scan_btn)
        
        select_all_btn = PushButton("全选")
        select_all_btn.clicked.connect(lambda: self._set_all_checked(True))
        btn_layout.addWidget(select_all_btn)
        
        deselect_btn = PushButton("取消全选")
        deselect_btn.clicked.connect(lambda: self._set_all_checked(False))
        btn_layout.addWidget(deselect_btn)
        
        btn_layout.addStretch()
        
        self.total_label = BodyLabel("")
        btn_layout.addWidget(self.total_label)
        
        clean_btn = PrimaryPushButton("开始清理")
        clean_btn.clicked.connect(self._start_clean)
        btn_layout.addWidget(clean_btn)
        
        content_layout.addLayout(btn_layout)
        
        # 进度
        self.progress_label = BodyLabel("")
        content_layout.addWidget(self.progress_label)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self._update_total()
    
    def _scan_all(self):
        """重新扫描"""
        for card in self.cards:
            card._scan_size()
        self._update_total()
        InfoBar.success("扫描完成", "已更新文件大小", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _set_all_checked(self, checked):
        for card in self.cards:
            card.checkbox.setChecked(checked)
    
    def _update_total(self):
        total = sum(card.size for card in self.cards if card.is_checked())
        self.total_label.setText(f"预计释放: {format_size(total)}")
    
    def _start_clean(self):
        """开始清理"""
        paths = []
        for card in self.cards:
            if card.is_checked():
                paths.extend(card.get_paths())
        
        if not paths:
            InfoBar.warning("提示", "请选择要清理的项目", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        self.progress_label.setText("正在清理...")
        self.clean_thread = CleanThread(paths)
        self.clean_thread.progress.connect(lambda msg: self.progress_label.setText(msg))
        self.clean_thread.finished.connect(self._on_clean_finished)
        self.clean_thread.start()
    
    def _on_clean_finished(self, files, size):
        self.progress_label.setText(f"清理完成: 删除 {files} 个文件，释放 {format_size(size)}")
        self._scan_all()
        InfoBar.success("清理完成", f"释放 {format_size(size)} 空间", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
