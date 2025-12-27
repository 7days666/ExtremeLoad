"""文本对比页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, TextEdit
)
import difflib


class TextDiffPage(QWidget):
    """文本对比页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("textDiffPage")
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.ALIGNMENT))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("文本对比"))
        title_layout.addStretch()
        
        compare_btn = PrimaryPushButton("对比")
        compare_btn.clicked.connect(self._compare)
        title_layout.addWidget(compare_btn)
        
        clear_btn = PushButton("清空")
        clear_btn.clicked.connect(self._clear)
        title_layout.addWidget(clear_btn)
        layout.addLayout(title_layout)
        
        # 输入区域
        input_splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(BodyLabel("原文本:"))
        self.left_text = TextEdit()
        self.left_text.setPlaceholderText("输入原文本...")
        left_layout.addWidget(self.left_text)
        input_splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(BodyLabel("新文本:"))
        self.right_text = TextEdit()
        self.right_text.setPlaceholderText("输入新文本...")
        right_layout.addWidget(self.right_text)
        input_splitter.addWidget(right_widget)
        
        layout.addWidget(input_splitter, 1)
        
        # 结果区域
        layout.addWidget(BodyLabel("对比结果:"))
        self.result_text = TextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.result_text, 1)

    
    def _compare(self):
        """对比文本"""
        left = self.left_text.toPlainText().splitlines(keepends=True)
        right = self.right_text.toPlainText().splitlines(keepends=True)
        
        if not left and not right:
            InfoBar.warning("提示", "请输入要对比的文本", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        diff = difflib.unified_diff(left, right, fromfile='原文本', tofile='新文本', lineterm='')
        result = '\n'.join(diff)
        
        if not result:
            result = "两段文本完全相同"
        
        self.result_text.setPlainText(result)
        
        # 统计差异
        added = sum(1 for line in result.split('\n') if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in result.split('\n') if line.startswith('-') and not line.startswith('---'))
        
        if added or removed:
            InfoBar.info("对比完成", f"新增 {added} 行，删除 {removed} 行", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _clear(self):
        """清空"""
        self.left_text.clear()
        self.right_text.clear()
        self.result_text.clear()
