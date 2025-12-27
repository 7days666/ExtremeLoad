"""IDE下载页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from qfluentwidgets import (
    CardWidget, PushButton, ProgressBar,
    TitleLabel, BodyLabel, InfoBar, InfoBarPosition,
    FluentIcon as FIF, IconWidget, CheckBox, LineEdit,
    ComboBox, PrimaryPushButton, SearchLineEdit
)
import requests
import os
import subprocess
import json
import winreg
from datetime import datetime


# 下载源配置（支持多版本）
DOWNLOAD_SOURCES = {
    "VSCode": {
        "name": "Visual Studio Code",
        "icon": FIF.CODE,
        "versions": {
            "最新稳定版": {
                "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
                "filename": "VSCodeSetup.exe"
            }
        },
        "detect_key": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{771FD6B0-FA20-440A-A002-3B3BAC16DC50}_is1",
        "detect_name": "Visual Studio Code"
    },
    "VS2022": {
        "name": "Visual Studio 2022",
        "icon": FIF.DEVELOPER_TOOLS,
        "versions": {
            "Community": {
                "url": "https://aka.ms/vs/17/release/vs_community.exe",
                "filename": "vs_community.exe"
            }
        },
        "detect_key": r"SOFTWARE\Microsoft\VisualStudio\17.0",
        "detect_name": "Visual Studio"
    },
    "Python": {
        "name": "Python",
        "icon": FIF.COMMAND_PROMPT,
        "versions": {
            "3.12.4": {
                "url": "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe",
                "filename": "python-3.12.4-amd64.exe"
            },
            "3.11.9": {
                "url": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe",
                "filename": "python-3.11.9-amd64.exe"
            },
            "3.10.14": {
                "url": "https://www.python.org/ftp/python/3.10.14/python-3.10.14-amd64.exe",
                "filename": "python-3.10.14-amd64.exe"
            }
        },
        "detect_cmd": "python --version",
        "detect_name": "Python"
    },
    "Node": {
        "name": "Node.js",
        "icon": FIF.APPLICATION,
        "versions": {
            "20.18.0 LTS": {
                "url": "https://npmmirror.com/mirrors/node/v20.18.0/node-v20.18.0-x64.msi",
                "filename": "node-v20.18.0-x64.msi"
            },
            "18.20.4 LTS": {
                "url": "https://npmmirror.com/mirrors/node/v18.20.4/node-v18.20.4-x64.msi",
                "filename": "node-v18.20.4-x64.msi"
            },
            "22.9.0 Current": {
                "url": "https://npmmirror.com/mirrors/node/v22.9.0/node-v22.9.0-x64.msi",
                "filename": "node-v22.9.0-x64.msi"
            }
        },
        "detect_cmd": "node --version",
        "detect_name": "Node.js"
    },
    "Git": {
        "name": "Git for Windows",
        "icon": FIF.GITHUB,
        "versions": {
            "2.46.0": {
                "url": "https://github.com/git-for-windows/git/releases/download/v2.46.0.windows.1/Git-2.46.0-64-bit.exe",
                "filename": "Git-2.46.0-64-bit.exe"
            }
        },
        "detect_cmd": "git --version",
        "detect_name": "Git"
    },
    "JDK": {
        "name": "JDK (Eclipse Temurin)",
        "icon": FIF.CAFE,
        "versions": {
            "21 LTS": {
                "url": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.4%2B7/OpenJDK21U-jdk_x64_windows_hotspot_21.0.4_7.msi",
                "filename": "OpenJDK21-jdk_x64_windows.msi"
            },
            "17 LTS": {
                "url": "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.12%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.12_7.msi",
                "filename": "OpenJDK17-jdk_x64_windows.msi"
            }
        },
        "detect_cmd": "java -version",
        "detect_name": "Java"
    },
    "Go": {
        "name": "Go",
        "icon": FIF.SPEED_HIGH,
        "versions": {
            "1.23.1": {
                "url": "https://go.dev/dl/go1.23.1.windows-amd64.msi",
                "filename": "go1.23.1.windows-amd64.msi"
            },
            "1.22.7": {
                "url": "https://go.dev/dl/go1.22.7.windows-amd64.msi",
                "filename": "go1.22.7.windows-amd64.msi"
            }
        },
        "detect_cmd": "go version",
        "detect_name": "Go"
    },
    "Rust": {
        "name": "Rust",
        "icon": FIF.SETTING,
        "versions": {
            "最新版": {
                "url": "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe",
                "filename": "rustup-init.exe"
            }
        },
        "detect_cmd": "rustc --version",
        "detect_name": "Rust"
    },
    "IDEA": {
        "name": "IntelliJ IDEA Community",
        "icon": FIF.BOOK_SHELF,
        "versions": {
            "2024.2": {
                "url": "https://download.jetbrains.com/idea/ideaIC-2024.2.exe",
                "filename": "ideaIC-2024.2.exe"
            }
        },
        "detect_key": r"SOFTWARE\JetBrains\IntelliJ IDEA",
        "detect_name": "IntelliJ IDEA"
    },
    "PyCharm": {
        "name": "PyCharm Community",
        "icon": FIF.BOOK_SHELF,
        "versions": {
            "2024.2": {
                "url": "https://download.jetbrains.com/python/pycharm-community-2024.2.exe",
                "filename": "pycharm-community-2024.2.exe"
            }
        },
        "detect_key": r"SOFTWARE\JetBrains\PyCharm",
        "detect_name": "PyCharm"
    }
}


def check_installed(info):
    """检测软件是否已安装"""
    # 通过命令检测
    if "detect_cmd" in info:
        try:
            result = subprocess.run(
                info["detect_cmd"], 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except:
            pass
    
    # 通过注册表检测
    if "detect_key" in info:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, info["detect_key"])
            return True
        except:
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, info["detect_key"])
                return True
            except:
                pass
    
    return False


class DownloadThread(QThread):
    """下载线程"""
    progress = pyqtSignal(int, int, int)  # percent, downloaded, total
    finished = pyqtSignal(bool, str)
    speed = pyqtSignal(str)
    
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
            last_downloaded = 0
            
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
                        
                        speed_bytes = downloaded - last_downloaded
                        last_downloaded = downloaded
                        if speed_bytes > 1024 * 1024:
                            self.speed.emit(f"{speed_bytes / 1024 / 1024:.1f} MB/s")
                        else:
                            self.speed.emit(f"{speed_bytes / 1024:.1f} KB/s")
            
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True


class DownloadCard(CardWidget):
    """下载卡片"""
    download_finished = pyqtSignal(str, str, str)  # name, version, path
    
    def __init__(self, key, info, get_save_dir, get_auto_open, parent=None):
        super().__init__(parent)
        self.key = key
        self.info = info
        self.get_save_dir = get_save_dir
        self.get_auto_open = get_auto_open
        self.download_thread = None
        self.current_save_path = None
        
        self._init_ui()
        self._check_installed()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        icon_widget = IconWidget(self.info["icon"])
        icon_widget.setFixedSize(28, 28)
        self.title_label = TitleLabel(self.info["name"])
        
        title_layout.addWidget(icon_widget)
        title_layout.addSpacing(10)
        title_layout.addWidget(self.title_label)
        
        # 已安装标识
        self.installed_label = BodyLabel("✓ 已安装")
        self.installed_label.setStyleSheet("color: #4CAF50;")
        self.installed_label.setVisible(False)
        title_layout.addWidget(self.installed_label)
        
        title_layout.addStretch()
        
        # 版本选择
        versions = list(self.info["versions"].keys())
        if len(versions) > 1:
            self.version_combo = ComboBox()
            self.version_combo.addItems(versions)
            self.version_combo.setMinimumWidth(160)
            title_layout.addWidget(self.version_combo)
        else:
            self.version_combo = None
            version_label = BodyLabel(versions[0])
            title_layout.addWidget(version_label)
        
        title_layout.addSpacing(10)
        
        # 下载按钮
        self.download_btn = PrimaryPushButton("下载")
        self.download_btn.setMinimumWidth(80)
        self.download_btn.clicked.connect(self._start_download)
        title_layout.addWidget(self.download_btn)
        
        # 取消按钮
        self.cancel_btn = PushButton("取消")
        self.cancel_btn.setMinimumWidth(80)
        self.cancel_btn.clicked.connect(self._cancel_download)
        self.cancel_btn.setVisible(False)
        title_layout.addWidget(self.cancel_btn)
        
        # 安装按钮
        self.install_btn = PushButton("安装")
        self.install_btn.setMinimumWidth(80)
        self.install_btn.clicked.connect(self._run_installer)
        self.install_btn.setVisible(False)
        title_layout.addWidget(self.install_btn)
        
        layout.addLayout(title_layout)
        
        # 进度行
        progress_layout = QHBoxLayout()
        
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar, 1)
        
        self.size_label = BodyLabel("")
        self.size_label.setVisible(False)
        self.size_label.setFixedWidth(150)
        progress_layout.addWidget(self.size_label)
        
        layout.addLayout(progress_layout)
        
        # 状态标签
        self.status_label = BodyLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        self.setFixedHeight(130)
    
    def _check_installed(self):
        """检测是否已安装"""
        installed = check_installed(self.info)
        self.installed_label.setVisible(installed)
    
    def _get_selected_version(self):
        if self.version_combo:
            return self.version_combo.currentText()
        return list(self.info["versions"].keys())[0]
    
    def _start_download(self):
        """开始下载"""
        save_dir = self.get_save_dir()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        version = self._get_selected_version()
        version_info = self.info["versions"][version]
        save_path = os.path.join(save_dir, version_info["filename"])
        self.current_save_path = save_path
        
        self.download_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.install_btn.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.size_label.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("正在连接...")
        
        self.download_thread = DownloadThread(version_info["url"], save_path)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.speed.connect(self._on_speed)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.start()
    
    def _cancel_download(self):
        """取消下载"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
    
    def _on_progress(self, percent, downloaded, total):
        self.progress_bar.setValue(percent)
        downloaded_mb = downloaded / 1024 / 1024
        total_mb = total / 1024 / 1024
        self.size_label.setText(f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB")
    
    def _on_speed(self, speed):
        self.status_label.setText(f"下载速度: {speed}")
    
    def _on_finished(self, success, message):
        self.download_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        
        if success:
            self.status_label.setText(f"下载完成")
            self.install_btn.setVisible(True)
            
            # 记录下载历史
            version = self._get_selected_version()
            self.download_finished.emit(self.info["name"], version, message)
            
            InfoBar.success(
                title="下载完成",
                content=f"{self.info['name']} 已保存",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000
            )
            
            if self.get_auto_open():
                folder = os.path.dirname(message)
                subprocess.Popen(f'explorer "{folder}"')
        else:
            self.status_label.setText(f"下载失败: {message}")
            self.progress_bar.setVisible(False)
            self.size_label.setVisible(False)
    
    def _run_installer(self):
        """运行安装程序"""
        if self.current_save_path and os.path.exists(self.current_save_path):
            subprocess.Popen(f'"{self.current_save_path}"', shell=True)
            InfoBar.info(
                title="正在启动安装程序",
                content="请在弹出的窗口中完成安装",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000
            )


class DownloadPage(QWidget):
    """IDE下载页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("downloadPage")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.history_file = os.path.join(os.path.expanduser("~"), ".extremeload_history.json")
        self.download_history = self._load_history()
        self._init_ui()
    
    def _load_history(self):
        """加载下载历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_history(self):
        """保存下载历史"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _add_history(self, name, version, path):
        """添加下载记录"""
        record = {
            "name": name,
            "version": version,
            "path": path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.download_history.insert(0, record)
        if len(self.download_history) > 50:
            self.download_history = self.download_history[:50]
        self._save_history()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)
        
        # 页面标题
        title_layout = QHBoxLayout()
        title_icon = IconWidget(FIF.DOWNLOAD)
        title_icon.setFixedSize(28, 28)
        title = TitleLabel("IDE 下载区")
        title_layout.addWidget(title_icon)
        title_layout.addSpacing(8)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # 搜索框
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索软件...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_cards)
        title_layout.addWidget(self.search_edit)
        title_layout.addSpacing(10)
        
        # 刷新检测按钮
        refresh_btn = PushButton("刷新检测")
        refresh_btn.clicked.connect(self._refresh_installed)
        title_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(title_layout)
        
        desc = BodyLabel("点击下载按钮，自动下载到指定文件夹，支持多任务同时下载")
        content_layout.addWidget(desc)
        
        # 设置区域
        settings_card = CardWidget()
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 15, 20, 15)
        
        path_layout = QHBoxLayout()
        path_label = BodyLabel("保存位置:")
        self.path_edit = LineEdit()
        self.path_edit.setText(self.save_dir)
        self.path_edit.setReadOnly(True)
        
        browse_btn = PushButton("浏览")
        browse_btn.clicked.connect(self._browse_folder)
        
        open_btn = PushButton("打开目录")
        open_btn.clicked.connect(self._open_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(browse_btn)
        path_layout.addWidget(open_btn)
        settings_layout.addLayout(path_layout)
        
        self.auto_open_checkbox = CheckBox("下载完成后自动打开目录")
        self.auto_open_checkbox.setChecked(True)
        settings_layout.addWidget(self.auto_open_checkbox)
        
        content_layout.addWidget(settings_card)
        
        # 下载卡片
        self.download_cards = []
        for key, info in DOWNLOAD_SOURCES.items():
            card = DownloadCard(key, info, self._get_save_dir, self._get_auto_open, self)
            card.download_finished.connect(self._add_history)
            self.download_cards.append(card)
            content_layout.addWidget(card)
        
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
        if os.path.exists(folder):
            subprocess.Popen(f'explorer "{folder}"')
        else:
            InfoBar.warning(
                title="目录不存在",
                content="请先选择有效的保存目录",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000
            )
    
    def _refresh_installed(self):
        """刷新已安装检测"""
        for card in self.download_cards:
            card._check_installed()
        InfoBar.success(
            title="刷新完成",
            content="已重新检测软件安装状态",
            parent=self.window(),
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000
        )
    
    def _filter_cards(self, text):
        """搜索过滤"""
        text = text.lower().strip()
        for card in self.download_cards:
            name = card.info["name"].lower()
            key = card.key.lower()
            if not text or text in name or text in key:
                card.setVisible(True)
            else:
                card.setVisible(False)
