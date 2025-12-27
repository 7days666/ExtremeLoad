"""Windows 优化页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, SwitchButton, ComboBox
)
import subprocess
import ctypes


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_cmd(cmd, admin=False):
    """运行命令"""
    try:
        if admin and not is_admin():
            return False, "需要管理员权限"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout or result.stderr
    except Exception as e:
        return False, str(e)


class WinOptPage(QWidget):
    """Windows 优化页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("winOptPage")
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
        title_layout.addWidget(IconWidget(FIF.SETTING))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("Windows 优化"))
        title_layout.addStretch()
        if not is_admin():
            admin_label = BodyLabel("⚠ 部分功能需要管理员权限")
            admin_label.setStyleSheet("color: #FF9800;")
            title_layout.addWidget(admin_label)
        content_layout.addLayout(title_layout)

        # 系统激活状态
        activate_card = CardWidget()
        activate_layout = QVBoxLayout(activate_card)
        activate_layout.setContentsMargins(20, 15, 20, 15)
        activate_layout.addWidget(TitleLabel("系统激活状态"))
        
        self.activate_label = BodyLabel("点击检测查看激活状态")
        activate_layout.addWidget(self.activate_label)
        
        activate_btn_layout = QHBoxLayout()
        check_btn = PushButton("检测激活状态")
        check_btn.clicked.connect(self._check_activation)
        activate_btn_layout.addWidget(check_btn)
        activate_btn_layout.addStretch()
        activate_layout.addLayout(activate_btn_layout)
        content_layout.addWidget(activate_card)
        
        # 防火墙
        firewall_card = CardWidget()
        firewall_layout = QVBoxLayout(firewall_card)
        firewall_layout.setContentsMargins(20, 15, 20, 15)
        firewall_layout.addWidget(TitleLabel("Windows 防火墙"))
        
        firewall_btn_layout = QHBoxLayout()
        self.firewall_status = BodyLabel("点击检测查看状态")
        firewall_btn_layout.addWidget(self.firewall_status)
        firewall_btn_layout.addStretch()
        
        check_fw_btn = PushButton("检测状态")
        check_fw_btn.clicked.connect(self._check_firewall)
        firewall_btn_layout.addWidget(check_fw_btn)
        
        enable_fw_btn = PushButton("启用防火墙")
        enable_fw_btn.clicked.connect(lambda: self._set_firewall(True))
        firewall_btn_layout.addWidget(enable_fw_btn)
        
        disable_fw_btn = PushButton("关闭防火墙")
        disable_fw_btn.clicked.connect(lambda: self._set_firewall(False))
        firewall_btn_layout.addWidget(disable_fw_btn)
        firewall_layout.addLayout(firewall_btn_layout)
        content_layout.addWidget(firewall_card)
        
        # 电源计划
        power_card = CardWidget()
        power_layout = QVBoxLayout(power_card)
        power_layout.setContentsMargins(20, 15, 20, 15)
        power_layout.addWidget(TitleLabel("电源计划"))
        
        power_btn_layout = QHBoxLayout()
        power_btn_layout.addWidget(BodyLabel("切换电源计划:"))
        
        balanced_btn = PushButton("平衡")
        balanced_btn.clicked.connect(lambda: self._set_power_plan("balanced"))
        power_btn_layout.addWidget(balanced_btn)
        
        high_btn = PushButton("高性能")
        high_btn.clicked.connect(lambda: self._set_power_plan("high"))
        power_btn_layout.addWidget(high_btn)
        
        save_btn = PushButton("节能")
        save_btn.clicked.connect(lambda: self._set_power_plan("saver"))
        power_btn_layout.addWidget(save_btn)
        
        power_btn_layout.addStretch()
        power_layout.addLayout(power_btn_layout)
        content_layout.addWidget(power_card)

        # Windows 功能
        feature_card = CardWidget()
        feature_layout = QVBoxLayout(feature_card)
        feature_layout.setContentsMargins(20, 15, 20, 15)
        feature_layout.addWidget(TitleLabel("Windows 功能"))
        feature_layout.addWidget(BodyLabel("启用/禁用 Windows 可选功能（需要管理员权限）"))
        
        features = [
            ("Microsoft-Hyper-V-All", "Hyper-V 虚拟化"),
            ("Microsoft-Windows-Subsystem-Linux", "WSL (Linux 子系统)"),
            ("VirtualMachinePlatform", "虚拟机平台"),
            ("Containers", "Windows 容器"),
        ]
        
        for feature_id, feature_name in features:
            feat_layout = QHBoxLayout()
            feat_layout.addWidget(BodyLabel(feature_name))
            feat_layout.addStretch()
            
            enable_btn = PushButton("启用")
            enable_btn.clicked.connect(lambda checked, f=feature_id: self._set_feature(f, True))
            feat_layout.addWidget(enable_btn)
            
            disable_btn = PushButton("禁用")
            disable_btn.clicked.connect(lambda checked, f=feature_id: self._set_feature(f, False))
            feat_layout.addWidget(disable_btn)
            
            feature_layout.addLayout(feat_layout)
        content_layout.addWidget(feature_card)
        
        # 快捷操作
        quick_card = CardWidget()
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(20, 15, 20, 15)
        quick_layout.addWidget(TitleLabel("快捷操作"))
        
        quick_btn_layout = QHBoxLayout()
        
        flush_dns_btn = PushButton("刷新 DNS 缓存")
        flush_dns_btn.clicked.connect(self._flush_dns)
        quick_btn_layout.addWidget(flush_dns_btn)
        
        reset_net_btn = PushButton("重置网络")
        reset_net_btn.clicked.connect(self._reset_network)
        quick_btn_layout.addWidget(reset_net_btn)
        
        open_services_btn = PushButton("打开服务管理")
        open_services_btn.clicked.connect(lambda: subprocess.Popen("services.msc"))
        quick_btn_layout.addWidget(open_services_btn)
        
        open_devmgmt_btn = PushButton("打开设备管理器")
        open_devmgmt_btn.clicked.connect(lambda: subprocess.Popen("devmgmt.msc"))
        quick_btn_layout.addWidget(open_devmgmt_btn)
        
        quick_btn_layout.addStretch()
        quick_layout.addLayout(quick_btn_layout)
        content_layout.addWidget(quick_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    
    def _check_activation(self):
        """检测激活状态"""
        success, output = run_cmd("slmgr /xpr")
        # slmgr 输出是弹窗，用 cscript 获取文本
        success, output = run_cmd('cscript //nologo "C:\\Windows\\System32\\slmgr.vbs" /xpr')
        if success:
            self.activate_label.setText(output.strip())
            if "永久" in output or "permanent" in output.lower():
                self.activate_label.setStyleSheet("color: #4CAF50;")
            else:
                self.activate_label.setStyleSheet("color: #FF9800;")
        else:
            self.activate_label.setText("检测失败")
    
    def _check_firewall(self):
        """检测防火墙状态"""
        success, output = run_cmd("netsh advfirewall show allprofiles state")
        if "ON" in output.upper():
            self.firewall_status.setText("✓ 防火墙已启用")
            self.firewall_status.setStyleSheet("color: #4CAF50;")
        else:
            self.firewall_status.setText("✗ 防火墙已关闭")
            self.firewall_status.setStyleSheet("color: #F44336;")
    
    def _set_firewall(self, enable):
        """设置防火墙"""
        state = "on" if enable else "off"
        success, output = run_cmd(f"netsh advfirewall set allprofiles state {state}", admin=True)
        if success:
            InfoBar.success("成功", f"防火墙已{'启用' if enable else '关闭'}", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            self._check_firewall()
        else:
            InfoBar.error("失败", output, parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _set_power_plan(self, plan):
        """设置电源计划"""
        plans = {
            "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "high": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "saver": "a1841308-3541-4fab-bc81-f71556f20b4a"
        }
        guid = plans.get(plan)
        success, output = run_cmd(f"powercfg /setactive {guid}")
        if success:
            InfoBar.success("成功", f"已切换到{'平衡' if plan == 'balanced' else '高性能' if plan == 'high' else '节能'}模式", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
        else:
            InfoBar.error("失败", output, parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _set_feature(self, feature, enable):
        """启用/禁用 Windows 功能"""
        action = "Enable" if enable else "Disable"
        cmd = f'dism /online /{action}-Feature /FeatureName:{feature} /NoRestart'
        InfoBar.info("执行中", "正在配置 Windows 功能，请稍候...", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        success, output = run_cmd(cmd, admin=True)
        if success:
            InfoBar.success("成功", f"功能已{'启用' if enable else '禁用'}，可能需要重启生效", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        else:
            InfoBar.error("失败", "需要管理员权限或功能不可用", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _flush_dns(self):
        """刷新 DNS"""
        success, output = run_cmd("ipconfig /flushdns")
        if success:
            InfoBar.success("成功", "DNS 缓存已刷新", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
        else:
            InfoBar.error("失败", output, parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _reset_network(self):
        """重置网络"""
        commands = [
            "netsh winsock reset",
            "netsh int ip reset",
            "ipconfig /release",
            "ipconfig /renew",
            "ipconfig /flushdns"
        ]
        for cmd in commands:
            run_cmd(cmd, admin=True)
        InfoBar.success("完成", "网络已重置，建议重启电脑", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
