"""Git 配置页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, SwitchButton
)
import subprocess


def run_git_cmd(cmd):
    """执行 git 命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def get_git_config(key):
    """获取 git 配置"""
    success, output = run_git_cmd(f'git config --global {key}')
    return output if success else ""


def set_git_config(key, value):
    """设置 git 配置"""
    return run_git_cmd(f'git config --global {key} "{value}"')


class GitConfigPage(QWidget):
    """Git 配置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gitConfigPage")
        self._init_ui()
        self._load_config()
    
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
        title_layout.addWidget(IconWidget(FIF.GITHUB))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("Git 配置"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        # 检测 Git 是否安装
        success, version = run_git_cmd("git --version")
        if success:
            content_layout.addWidget(BodyLabel(f"✓ {version}"))
        else:
            content_layout.addWidget(BodyLabel("⚠ Git 未安装，请先安装 Git"))
        
        # 用户信息配置
        user_card = CardWidget()
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(20, 15, 20, 15)
        user_layout.setSpacing(12)
        user_layout.addWidget(TitleLabel("用户信息"))
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(BodyLabel("用户名:"))
        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText("Your Name")
        self.name_edit.setMinimumWidth(300)
        name_layout.addWidget(self.name_edit)
        name_layout.addStretch()
        user_layout.addLayout(name_layout)
        
        email_layout = QHBoxLayout()
        email_layout.addWidget(BodyLabel("邮箱:"))
        self.email_edit = LineEdit()
        self.email_edit.setPlaceholderText("your@email.com")
        self.email_edit.setMinimumWidth(300)
        email_layout.addWidget(self.email_edit)
        email_layout.addStretch()
        user_layout.addLayout(email_layout)
        
        save_user_btn = PrimaryPushButton("保存用户信息")
        save_user_btn.clicked.connect(self._save_user_info)
        user_layout.addWidget(save_user_btn)
        content_layout.addWidget(user_card)

        # 代理配置
        proxy_card = CardWidget()
        proxy_layout = QVBoxLayout(proxy_card)
        proxy_layout.setContentsMargins(20, 15, 20, 15)
        proxy_layout.setSpacing(12)
        proxy_layout.addWidget(TitleLabel("代理配置"))
        
        proxy_enable_layout = QHBoxLayout()
        proxy_enable_layout.addWidget(BodyLabel("启用代理:"))
        self.proxy_switch = SwitchButton()
        proxy_enable_layout.addWidget(self.proxy_switch)
        proxy_enable_layout.addStretch()
        proxy_layout.addLayout(proxy_enable_layout)
        
        http_proxy_layout = QHBoxLayout()
        http_proxy_layout.addWidget(BodyLabel("HTTP 代理:"))
        self.http_proxy_edit = LineEdit()
        self.http_proxy_edit.setPlaceholderText("http://127.0.0.1:7890")
        self.http_proxy_edit.setMinimumWidth(300)
        http_proxy_layout.addWidget(self.http_proxy_edit)
        http_proxy_layout.addStretch()
        proxy_layout.addLayout(http_proxy_layout)
        
        https_proxy_layout = QHBoxLayout()
        https_proxy_layout.addWidget(BodyLabel("HTTPS 代理:"))
        self.https_proxy_edit = LineEdit()
        self.https_proxy_edit.setPlaceholderText("http://127.0.0.1:7890")
        self.https_proxy_edit.setMinimumWidth(300)
        https_proxy_layout.addWidget(self.https_proxy_edit)
        https_proxy_layout.addStretch()
        proxy_layout.addLayout(https_proxy_layout)
        
        proxy_btn_layout = QHBoxLayout()
        save_proxy_btn = PrimaryPushButton("保存代理")
        save_proxy_btn.clicked.connect(self._save_proxy)
        proxy_btn_layout.addWidget(save_proxy_btn)
        
        clear_proxy_btn = PushButton("清除代理")
        clear_proxy_btn.clicked.connect(self._clear_proxy)
        proxy_btn_layout.addWidget(clear_proxy_btn)
        proxy_btn_layout.addStretch()
        proxy_layout.addLayout(proxy_btn_layout)
        content_layout.addWidget(proxy_card)

        # 常用配置
        common_card = CardWidget()
        common_layout = QVBoxLayout(common_card)
        common_layout.setContentsMargins(20, 15, 20, 15)
        common_layout.setSpacing(12)
        common_layout.addWidget(TitleLabel("常用配置"))
        
        # 换行符配置
        crlf_layout = QHBoxLayout()
        crlf_layout.addWidget(BodyLabel("自动转换换行符 (autocrlf):"))
        self.crlf_switch = SwitchButton()
        crlf_layout.addWidget(self.crlf_switch)
        crlf_layout.addStretch()
        common_layout.addLayout(crlf_layout)
        
        # 凭证存储
        credential_layout = QHBoxLayout()
        credential_layout.addWidget(BodyLabel("记住密码 (credential.helper):"))
        self.credential_switch = SwitchButton()
        credential_layout.addWidget(self.credential_switch)
        credential_layout.addStretch()
        common_layout.addLayout(credential_layout)
        
        save_common_btn = PrimaryPushButton("保存常用配置")
        save_common_btn.clicked.connect(self._save_common)
        common_layout.addWidget(save_common_btn)
        content_layout.addWidget(common_card)
        
        # SSH 密钥
        ssh_card = CardWidget()
        ssh_layout = QVBoxLayout(ssh_card)
        ssh_layout.setContentsMargins(20, 15, 20, 15)
        ssh_layout.setSpacing(12)
        ssh_layout.addWidget(TitleLabel("SSH 密钥"))
        ssh_layout.addWidget(BodyLabel("生成 SSH 密钥用于 GitHub/GitLab 等平台"))
        
        ssh_btn_layout = QHBoxLayout()
        gen_ssh_btn = PushButton("生成 SSH 密钥")
        gen_ssh_btn.clicked.connect(self._generate_ssh)
        ssh_btn_layout.addWidget(gen_ssh_btn)
        
        open_ssh_btn = PushButton("打开 .ssh 目录")
        open_ssh_btn.clicked.connect(self._open_ssh_dir)
        ssh_btn_layout.addWidget(open_ssh_btn)
        ssh_btn_layout.addStretch()
        ssh_layout.addLayout(ssh_btn_layout)
        content_layout.addWidget(ssh_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    
    def _load_config(self):
        """加载当前配置"""
        self.name_edit.setText(get_git_config("user.name"))
        self.email_edit.setText(get_git_config("user.email"))
        
        http_proxy = get_git_config("http.proxy")
        https_proxy = get_git_config("https.proxy")
        self.http_proxy_edit.setText(http_proxy)
        self.https_proxy_edit.setText(https_proxy)
        self.proxy_switch.setChecked(bool(http_proxy or https_proxy))
        
        autocrlf = get_git_config("core.autocrlf")
        self.crlf_switch.setChecked(autocrlf.lower() == "true")
        
        credential = get_git_config("credential.helper")
        self.credential_switch.setChecked(bool(credential))
    
    def _save_user_info(self):
        """保存用户信息"""
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        
        if not name or not email:
            InfoBar.warning("提示", "请填写用户名和邮箱", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        set_git_config("user.name", name)
        set_git_config("user.email", email)
        InfoBar.success("保存成功", "Git 用户信息已更新", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _save_proxy(self):
        """保存代理配置"""
        http_proxy = self.http_proxy_edit.text().strip()
        https_proxy = self.https_proxy_edit.text().strip() or http_proxy
        
        if self.proxy_switch.isChecked() and http_proxy:
            set_git_config("http.proxy", http_proxy)
            set_git_config("https.proxy", https_proxy)
            InfoBar.success("保存成功", "Git 代理已配置", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
        else:
            self._clear_proxy()
    
    def _clear_proxy(self):
        """清除代理"""
        run_git_cmd("git config --global --unset http.proxy")
        run_git_cmd("git config --global --unset https.proxy")
        self.http_proxy_edit.clear()
        self.https_proxy_edit.clear()
        self.proxy_switch.setChecked(False)
        InfoBar.success("清除成功", "Git 代理已清除", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _save_common(self):
        """保存常用配置"""
        set_git_config("core.autocrlf", "true" if self.crlf_switch.isChecked() else "false")
        if self.credential_switch.isChecked():
            set_git_config("credential.helper", "store")
        else:
            run_git_cmd("git config --global --unset credential.helper")
        InfoBar.success("保存成功", "Git 配置已更新", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
    
    def _generate_ssh(self):
        """生成 SSH 密钥"""
        import os
        email = self.email_edit.text().strip() or "your@email.com"
        ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
        key_path = os.path.join(ssh_dir, "id_ed25519")
        
        if os.path.exists(key_path):
            InfoBar.warning("提示", "SSH 密钥已存在，如需重新生成请先删除", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
            return
        
        success, output = run_git_cmd(f'ssh-keygen -t ed25519 -C "{email}" -f "{key_path}" -N ""')
        if success:
            InfoBar.success("生成成功", "SSH 密钥已生成，请将公钥添加到 GitHub", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        else:
            InfoBar.error("生成失败", output, parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _open_ssh_dir(self):
        """打开 .ssh 目录"""
        import os
        import subprocess
        ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
        subprocess.Popen(f'explorer "{ssh_dir}"')
