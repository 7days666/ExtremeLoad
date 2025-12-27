"""文件哈希计算页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, TextEdit, ProgressBar
)
import hashlib
import os


class HashThread(QThread):
    """哈希计算线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
    
    def run(self):
        try:
            file_size = os.path.getsize(self.filepath)
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            
            read_size = 0
            with open(self.filepath, 'rb') as f:
                while chunk := f.read(8192):
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha256.update(chunk)
                    read_size += len(chunk)
                    if file_size > 0:
                        self.progress.emit(int(read_size * 100 / file_size))
            
            self.finished.emit({
                "md5": md5.hexdigest(),
                "sha1": sha1.hexdigest(),
                "sha256": sha256.hexdigest(),
                "size": file_size
            })
        except Exception as e:
            self.finished.emit({"error": str(e)})


class HashPage(QWidget):
    """文件哈希计算页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hashPage")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.FINGERPRINT))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("文件哈希计算"))
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        layout.addWidget(BodyLabel("计算文件的 MD5、SHA1、SHA256 哈希值"))
        
        # 文件选择
        file_card = CardWidget()
        file_layout = QVBoxLayout(file_card)
        file_layout.setContentsMargins(20, 15, 20, 15)
        
        select_layout = QHBoxLayout()
        self.file_edit = LineEdit()
        self.file_edit.setPlaceholderText("选择或拖入文件...")
        self.file_edit.setReadOnly(True)
        select_layout.addWidget(self.file_edit, 1)
        
        browse_btn = PushButton("浏览")
        browse_btn.clicked.connect(self._browse_file)
        select_layout.addWidget(browse_btn)
        
        calc_btn = PrimaryPushButton("计算")
        calc_btn.clicked.connect(self._calculate)
        select_layout.addWidget(calc_btn)
        file_layout.addLayout(select_layout)
        
        self.progress = ProgressBar()
        self.progress.setVisible(False)
        file_layout.addWidget(self.progress)
        layout.addWidget(file_card)
        
        # 结果显示
        result_card = CardWidget()
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(20, 15, 20, 15)
        result_layout.addWidget(TitleLabel("计算结果"))
        
        self.size_label = BodyLabel("文件大小: -")
        result_layout.addWidget(self.size_label)
        
        for name in ["MD5", "SHA1", "SHA256"]:
            h_layout = QHBoxLayout()
            h_layout.addWidget(BodyLabel(f"{name}:"))
            edit = LineEdit()
            edit.setReadOnly(True)
            setattr(self, f"{name.lower()}_edit", edit)
            h_layout.addWidget(edit, 1)
            copy_btn = PushButton("复制")
            copy_btn.clicked.connect(lambda checked, e=edit: self._copy(e.text()))
            h_layout.addWidget(copy_btn)
            result_layout.addLayout(h_layout)
        
        layout.addWidget(result_card)

        # 校验对比
        verify_card = CardWidget()
        verify_layout = QVBoxLayout(verify_card)
        verify_layout.setContentsMargins(20, 15, 20, 15)
        verify_layout.addWidget(TitleLabel("哈希校验"))
        
        verify_input_layout = QHBoxLayout()
        self.verify_edit = LineEdit()
        self.verify_edit.setPlaceholderText("粘贴要校验的哈希值...")
        verify_input_layout.addWidget(self.verify_edit, 1)
        
        verify_btn = PushButton("校验")
        verify_btn.clicked.connect(self._verify)
        verify_input_layout.addWidget(verify_btn)
        verify_layout.addLayout(verify_input_layout)
        
        self.verify_result = BodyLabel("")
        verify_layout.addWidget(self.verify_result)
        layout.addWidget(verify_card)
        
        layout.addStretch()
    
    def _browse_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if filepath:
            self.file_edit.setText(filepath)
    
    def _calculate(self):
        filepath = self.file_edit.text()
        if not filepath or not os.path.exists(filepath):
            InfoBar.warning("提示", "请选择有效文件", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.hash_thread = HashThread(filepath)
        self.hash_thread.progress.connect(self.progress.setValue)
        self.hash_thread.finished.connect(self._on_finished)
        self.hash_thread.start()
    
    def _on_finished(self, result):
        self.progress.setVisible(False)
        if "error" in result:
            InfoBar.error("错误", result["error"], parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
            return
        
        size = result["size"]
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024*1024:
            size_str = f"{size/1024:.2f} KB"
        elif size < 1024*1024*1024:
            size_str = f"{size/1024/1024:.2f} MB"
        else:
            size_str = f"{size/1024/1024/1024:.2f} GB"
        
        self.size_label.setText(f"文件大小: {size_str}")
        self.md5_edit.setText(result["md5"])
        self.sha1_edit.setText(result["sha1"])
        self.sha256_edit.setText(result["sha256"])
        InfoBar.success("完成", "哈希计算完成", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _copy(self, text):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        InfoBar.success("已复制", "", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=1500)
    
    def _verify(self):
        input_hash = self.verify_edit.text().strip().lower()
        if not input_hash:
            return
        
        md5 = self.md5_edit.text().lower()
        sha1 = self.sha1_edit.text().lower()
        sha256 = self.sha256_edit.text().lower()
        
        if input_hash == md5:
            self.verify_result.setText("✓ MD5 匹配")
            self.verify_result.setStyleSheet("color: #4CAF50;")
        elif input_hash == sha1:
            self.verify_result.setText("✓ SHA1 匹配")
            self.verify_result.setStyleSheet("color: #4CAF50;")
        elif input_hash == sha256:
            self.verify_result.setText("✓ SHA256 匹配")
            self.verify_result.setStyleSheet("color: #4CAF50;")
        else:
            self.verify_result.setText("✗ 不匹配")
            self.verify_result.setStyleSheet("color: #F44336;")
