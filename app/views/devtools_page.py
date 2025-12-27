"""开发工具页面 - UUID/密码生成、数据库测试、API测试"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, ComboBox, SpinBox, TextEdit
)
import uuid
import secrets
import string
import json
import requests


class DevToolsPage(QWidget):
    """开发工具页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("devToolsPage")
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
        title_layout.addWidget(IconWidget(FIF.DEVELOPER_TOOLS))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("开发工具"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)

        # UUID 生成器
        uuid_card = CardWidget()
        uuid_layout = QVBoxLayout(uuid_card)
        uuid_layout.setContentsMargins(20, 15, 20, 15)
        uuid_layout.addWidget(TitleLabel("UUID 生成器"))
        
        uuid_btn_layout = QHBoxLayout()
        self.uuid_edit = LineEdit()
        self.uuid_edit.setReadOnly(True)
        uuid_btn_layout.addWidget(self.uuid_edit, 1)
        
        uuid1_btn = PushButton("UUID1")
        uuid1_btn.clicked.connect(lambda: self.uuid_edit.setText(str(uuid.uuid1())))
        uuid_btn_layout.addWidget(uuid1_btn)
        
        uuid4_btn = PushButton("UUID4")
        uuid4_btn.clicked.connect(lambda: self.uuid_edit.setText(str(uuid.uuid4())))
        uuid_btn_layout.addWidget(uuid4_btn)
        
        copy_uuid_btn = PushButton("复制")
        copy_uuid_btn.clicked.connect(lambda: self._copy_text(self.uuid_edit.text()))
        uuid_btn_layout.addWidget(copy_uuid_btn)
        uuid_layout.addLayout(uuid_btn_layout)
        content_layout.addWidget(uuid_card)
        
        # 密码生成器
        pwd_card = CardWidget()
        pwd_layout = QVBoxLayout(pwd_card)
        pwd_layout.setContentsMargins(20, 15, 20, 15)
        pwd_layout.addWidget(TitleLabel("密码生成器"))
        
        pwd_opt_layout = QHBoxLayout()
        pwd_opt_layout.addWidget(BodyLabel("长度:"))
        self.pwd_len_spin = SpinBox()
        self.pwd_len_spin.setRange(6, 64)
        self.pwd_len_spin.setValue(16)
        pwd_opt_layout.addWidget(self.pwd_len_spin)
        
        pwd_opt_layout.addWidget(BodyLabel("类型:"))
        self.pwd_type_combo = ComboBox()
        self.pwd_type_combo.addItems(["字母+数字+符号", "字母+数字", "纯数字", "纯字母"])
        pwd_opt_layout.addWidget(self.pwd_type_combo)
        pwd_opt_layout.addStretch()
        pwd_layout.addLayout(pwd_opt_layout)
        
        pwd_result_layout = QHBoxLayout()
        self.pwd_edit = LineEdit()
        self.pwd_edit.setReadOnly(True)
        pwd_result_layout.addWidget(self.pwd_edit, 1)
        
        gen_pwd_btn = PrimaryPushButton("生成")
        gen_pwd_btn.clicked.connect(self._generate_password)
        pwd_result_layout.addWidget(gen_pwd_btn)
        
        copy_pwd_btn = PushButton("复制")
        copy_pwd_btn.clicked.connect(lambda: self._copy_text(self.pwd_edit.text()))
        pwd_result_layout.addWidget(copy_pwd_btn)
        pwd_layout.addLayout(pwd_result_layout)
        content_layout.addWidget(pwd_card)

        # API 测试
        api_card = CardWidget()
        api_layout = QVBoxLayout(api_card)
        api_layout.setContentsMargins(20, 15, 20, 15)
        api_layout.addWidget(TitleLabel("API 测试"))
        
        api_url_layout = QHBoxLayout()
        self.api_method = ComboBox()
        self.api_method.addItems(["GET", "POST", "PUT", "DELETE"])
        self.api_method.setFixedWidth(80)
        api_url_layout.addWidget(self.api_method)
        
        self.api_url = LineEdit()
        self.api_url.setPlaceholderText("https://api.example.com/endpoint")
        api_url_layout.addWidget(self.api_url, 1)
        
        send_btn = PrimaryPushButton("发送")
        send_btn.clicked.connect(self._send_request)
        api_url_layout.addWidget(send_btn)
        api_layout.addLayout(api_url_layout)
        
        api_body_layout = QHBoxLayout()
        api_body_layout.addWidget(BodyLabel("请求体 (JSON):"))
        api_layout.addLayout(api_body_layout)
        
        self.api_body = TextEdit()
        self.api_body.setPlaceholderText('{"key": "value"}')
        self.api_body.setMaximumHeight(80)
        api_layout.addWidget(self.api_body)
        
        api_layout.addWidget(BodyLabel("响应:"))
        self.api_response = TextEdit()
        self.api_response.setReadOnly(True)
        self.api_response.setMaximumHeight(150)
        api_layout.addWidget(self.api_response)
        content_layout.addWidget(api_card)
        
        # 数据库连接测试
        db_card = CardWidget()
        db_layout = QVBoxLayout(db_card)
        db_layout.setContentsMargins(20, 15, 20, 15)
        db_layout.addWidget(TitleLabel("数据库连接测试"))
        
        db_type_layout = QHBoxLayout()
        db_type_layout.addWidget(BodyLabel("类型:"))
        self.db_type = ComboBox()
        self.db_type.addItems(["MySQL", "PostgreSQL", "Redis", "MongoDB"])
        self.db_type.setFixedWidth(120)
        db_type_layout.addWidget(self.db_type)
        
        db_type_layout.addWidget(BodyLabel("主机:"))
        self.db_host = LineEdit()
        self.db_host.setText("127.0.0.1")
        self.db_host.setFixedWidth(150)
        db_type_layout.addWidget(self.db_host)
        
        db_type_layout.addWidget(BodyLabel("端口:"))
        self.db_port = LineEdit()
        self.db_port.setText("3306")
        self.db_port.setFixedWidth(80)
        db_type_layout.addWidget(self.db_port)
        db_type_layout.addStretch()
        db_layout.addLayout(db_type_layout)

        db_auth_layout = QHBoxLayout()
        db_auth_layout.addWidget(BodyLabel("用户名:"))
        self.db_user = LineEdit()
        self.db_user.setText("root")
        self.db_user.setFixedWidth(120)
        db_auth_layout.addWidget(self.db_user)
        
        db_auth_layout.addWidget(BodyLabel("密码:"))
        self.db_pwd = LineEdit()
        self.db_pwd.setEchoMode(LineEdit.Password)
        self.db_pwd.setFixedWidth(150)
        db_auth_layout.addWidget(self.db_pwd)
        
        test_db_btn = PrimaryPushButton("测试连接")
        test_db_btn.clicked.connect(self._test_db_connection)
        db_auth_layout.addWidget(test_db_btn)
        db_auth_layout.addStretch()
        db_layout.addLayout(db_auth_layout)
        
        self.db_result = BodyLabel("")
        db_layout.addWidget(self.db_result)
        content_layout.addWidget(db_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _copy_text(self, text):
        """复制到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        InfoBar.success("已复制", "", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=1500)
    
    def _generate_password(self):
        """生成密码"""
        length = self.pwd_len_spin.value()
        pwd_type = self.pwd_type_combo.currentIndex()
        
        if pwd_type == 0:  # 字母+数字+符号
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
        elif pwd_type == 1:  # 字母+数字
            chars = string.ascii_letters + string.digits
        elif pwd_type == 2:  # 纯数字
            chars = string.digits
        else:  # 纯字母
            chars = string.ascii_letters
        
        password = ''.join(secrets.choice(chars) for _ in range(length))
        self.pwd_edit.setText(password)

    
    def _send_request(self):
        """发送 HTTP 请求"""
        url = self.api_url.text().strip()
        if not url:
            InfoBar.warning("提示", "请输入 URL", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        method = self.api_method.currentText()
        body = self.api_body.toPlainText().strip()
        
        try:
            headers = {"Content-Type": "application/json"}
            data = json.loads(body) if body else None
            
            if method == "GET":
                resp = requests.get(url, timeout=10)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == "PUT":
                resp = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                resp = requests.delete(url, timeout=10)
            
            result = f"状态码: {resp.status_code}\n\n"
            try:
                result += json.dumps(resp.json(), indent=2, ensure_ascii=False)
            except:
                result += resp.text[:1000]
            
            self.api_response.setPlainText(result)
        except Exception as e:
            self.api_response.setPlainText(f"请求失败: {str(e)}")
    
    def _test_db_connection(self):
        """测试数据库连接"""
        db_type = self.db_type.currentText()
        host = self.db_host.text().strip()
        port = self.db_port.text().strip()
        user = self.db_user.text().strip()
        pwd = self.db_pwd.text()
        
        self.db_result.setText("正在连接...")
        self.db_result.setStyleSheet("")
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            
            if result == 0:
                self.db_result.setText(f"✓ 端口 {port} 可访问（完整连接测试需安装对应数据库驱动）")
                self.db_result.setStyleSheet("color: #4CAF50;")
            else:
                self.db_result.setText(f"✗ 无法连接到 {host}:{port}")
                self.db_result.setStyleSheet("color: #F44336;")
        except Exception as e:
            self.db_result.setText(f"✗ 连接失败: {str(e)}")
            self.db_result.setStyleSheet("color: #F44336;")
