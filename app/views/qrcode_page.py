"""二维码生成页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, TextEdit
)
import io

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


class QRCodePage(QWidget):
    """二维码生成页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("qrcodePage")
        self.qr_image = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.QRCODE))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("二维码工具"))
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        if not HAS_QRCODE:
            layout.addWidget(BodyLabel("⚠ 需要安装 qrcode 库: pip install qrcode[pil]"))
            layout.addStretch()
            return
        
        # 生成二维码
        gen_card = CardWidget()
        gen_layout = QVBoxLayout(gen_card)
        gen_layout.setContentsMargins(20, 15, 20, 15)
        gen_layout.addWidget(TitleLabel("生成二维码"))
        
        self.text_input = TextEdit()
        self.text_input.setPlaceholderText("输入文本或网址...")
        self.text_input.setMaximumHeight(80)
        gen_layout.addWidget(self.text_input)
        
        btn_layout = QHBoxLayout()
        gen_btn = PrimaryPushButton("生成")
        gen_btn.clicked.connect(self._generate)
        btn_layout.addWidget(gen_btn)
        
        save_btn = PushButton("保存图片")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        gen_layout.addLayout(btn_layout)
        
        # 二维码显示
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(200, 200)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("background: white; border: 1px solid #ccc;")
        gen_layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)
        
        layout.addWidget(gen_card)
        layout.addStretch()

    
    def _generate(self):
        """生成二维码"""
        text = self.text_input.toPlainText().strip()
        if not text:
            InfoBar.warning("提示", "请输入内容", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为 QPixmap
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            qimage = QImage()
            qimage.loadFromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)
            
            self.qr_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.qr_image = img
            
            InfoBar.success("成功", "二维码已生成", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
        except Exception as e:
            InfoBar.error("错误", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _save(self):
        """保存二维码"""
        if not self.qr_image:
            InfoBar.warning("提示", "请先生成二维码", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        filepath, _ = QFileDialog.getSaveFileName(self, "保存二维码", "qrcode.png", "PNG (*.png)")
        if filepath:
            self.qr_image.save(filepath)
            InfoBar.success("成功", f"已保存到 {filepath}", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
