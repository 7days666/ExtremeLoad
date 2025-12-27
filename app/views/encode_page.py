"""编码转换页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, TextEdit, ComboBox
)
import base64
import urllib.parse
import json
import html


class EncodePage(QWidget):
    """编码转换页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("encodePage")
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
        title_layout.addWidget(IconWidget(FIF.LANGUAGE))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("编码转换"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)

        # Base64
        base64_card = CardWidget()
        base64_layout = QVBoxLayout(base64_card)
        base64_layout.setContentsMargins(20, 15, 20, 15)
        base64_layout.addWidget(TitleLabel("Base64 编码/解码"))
        
        self.base64_input = TextEdit()
        self.base64_input.setPlaceholderText("输入文本...")
        self.base64_input.setMaximumHeight(80)
        base64_layout.addWidget(self.base64_input)
        
        base64_btn_layout = QHBoxLayout()
        encode_b64_btn = PrimaryPushButton("编码")
        encode_b64_btn.clicked.connect(self._base64_encode)
        base64_btn_layout.addWidget(encode_b64_btn)
        decode_b64_btn = PushButton("解码")
        decode_b64_btn.clicked.connect(self._base64_decode)
        base64_btn_layout.addWidget(decode_b64_btn)
        base64_btn_layout.addStretch()
        base64_layout.addLayout(base64_btn_layout)
        
        self.base64_output = TextEdit()
        self.base64_output.setReadOnly(True)
        self.base64_output.setMaximumHeight(80)
        base64_layout.addWidget(self.base64_output)
        content_layout.addWidget(base64_card)
        
        # URL 编码
        url_card = CardWidget()
        url_layout = QVBoxLayout(url_card)
        url_layout.setContentsMargins(20, 15, 20, 15)
        url_layout.addWidget(TitleLabel("URL 编码/解码"))
        
        self.url_input = TextEdit()
        self.url_input.setPlaceholderText("输入 URL 或文本...")
        self.url_input.setMaximumHeight(80)
        url_layout.addWidget(self.url_input)
        
        url_btn_layout = QHBoxLayout()
        encode_url_btn = PrimaryPushButton("编码")
        encode_url_btn.clicked.connect(self._url_encode)
        url_btn_layout.addWidget(encode_url_btn)
        decode_url_btn = PushButton("解码")
        decode_url_btn.clicked.connect(self._url_decode)
        url_btn_layout.addWidget(decode_url_btn)
        url_btn_layout.addStretch()
        url_layout.addLayout(url_btn_layout)
        
        self.url_output = TextEdit()
        self.url_output.setReadOnly(True)
        self.url_output.setMaximumHeight(80)
        url_layout.addWidget(self.url_output)
        content_layout.addWidget(url_card)

        # JSON 格式化
        json_card = CardWidget()
        json_layout = QVBoxLayout(json_card)
        json_layout.setContentsMargins(20, 15, 20, 15)
        json_layout.addWidget(TitleLabel("JSON 格式化"))
        
        self.json_input = TextEdit()
        self.json_input.setPlaceholderText('{"key": "value"}')
        self.json_input.setMaximumHeight(100)
        json_layout.addWidget(self.json_input)
        
        json_btn_layout = QHBoxLayout()
        format_btn = PrimaryPushButton("格式化")
        format_btn.clicked.connect(self._json_format)
        json_btn_layout.addWidget(format_btn)
        compress_btn = PushButton("压缩")
        compress_btn.clicked.connect(self._json_compress)
        json_btn_layout.addWidget(compress_btn)
        json_btn_layout.addStretch()
        json_layout.addLayout(json_btn_layout)
        
        self.json_output = TextEdit()
        self.json_output.setReadOnly(True)
        self.json_output.setMaximumHeight(150)
        json_layout.addWidget(self.json_output)
        content_layout.addWidget(json_card)
        
        # HTML 转义
        html_card = CardWidget()
        html_layout = QVBoxLayout(html_card)
        html_layout.setContentsMargins(20, 15, 20, 15)
        html_layout.addWidget(TitleLabel("HTML 转义"))
        
        self.html_input = TextEdit()
        self.html_input.setPlaceholderText("<div>Hello</div>")
        self.html_input.setMaximumHeight(80)
        html_layout.addWidget(self.html_input)
        
        html_btn_layout = QHBoxLayout()
        escape_btn = PrimaryPushButton("转义")
        escape_btn.clicked.connect(self._html_escape)
        html_btn_layout.addWidget(escape_btn)
        unescape_btn = PushButton("反转义")
        unescape_btn.clicked.connect(self._html_unescape)
        html_btn_layout.addWidget(unescape_btn)
        html_btn_layout.addStretch()
        html_layout.addLayout(html_btn_layout)
        
        self.html_output = TextEdit()
        self.html_output.setReadOnly(True)
        self.html_output.setMaximumHeight(80)
        html_layout.addWidget(self.html_output)
        content_layout.addWidget(html_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    
    def _base64_encode(self):
        text = self.base64_input.toPlainText()
        try:
            result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            self.base64_output.setPlainText(result)
        except Exception as e:
            self.base64_output.setPlainText(f"错误: {e}")
    
    def _base64_decode(self):
        text = self.base64_input.toPlainText()
        try:
            result = base64.b64decode(text).decode('utf-8')
            self.base64_output.setPlainText(result)
        except Exception as e:
            self.base64_output.setPlainText(f"错误: {e}")
    
    def _url_encode(self):
        text = self.url_input.toPlainText()
        result = urllib.parse.quote(text, safe='')
        self.url_output.setPlainText(result)
    
    def _url_decode(self):
        text = self.url_input.toPlainText()
        try:
            result = urllib.parse.unquote(text)
            self.url_output.setPlainText(result)
        except Exception as e:
            self.url_output.setPlainText(f"错误: {e}")
    
    def _json_format(self):
        text = self.json_input.toPlainText()
        try:
            obj = json.loads(text)
            result = json.dumps(obj, indent=2, ensure_ascii=False)
            self.json_output.setPlainText(result)
        except Exception as e:
            self.json_output.setPlainText(f"JSON 解析错误: {e}")
    
    def _json_compress(self):
        text = self.json_input.toPlainText()
        try:
            obj = json.loads(text)
            result = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
            self.json_output.setPlainText(result)
        except Exception as e:
            self.json_output.setPlainText(f"JSON 解析错误: {e}")
    
    def _html_escape(self):
        text = self.html_input.toPlainText()
        result = html.escape(text)
        self.html_output.setPlainText(result)
    
    def _html_unescape(self):
        text = self.html_input.toPlainText()
        result = html.unescape(text)
        self.html_output.setPlainText(result)
