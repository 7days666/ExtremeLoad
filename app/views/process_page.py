"""进程管理页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, SearchLineEdit, CheckBox
)
import subprocess
import os


class ProcessThread(QThread):
    """获取进程列表线程"""
    finished = pyqtSignal(list)
    
    def run(self):
        try:
            result = subprocess.run(
                'wmic process get ProcessId,Name,WorkingSetSize,CommandLine /format:csv',
                shell=True, capture_output=True, text=True, timeout=30
            )
            lines = result.stdout.strip().split('\n')
            processes = []
            for line in lines[1:]:  # 跳过头部
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    try:
                        cmd = parts[1] if len(parts) > 1 else ""
                        name = parts[2] if len(parts) > 2 else ""
                        pid = parts[3] if len(parts) > 3 else ""
                        mem = parts[4] if len(parts) > 4 else "0"
                        
                        if name and pid:
                            mem_mb = int(mem) / 1024 / 1024 if mem.isdigit() else 0
                            processes.append({
                                "name": name,
                                "pid": pid,
                                "memory": f"{mem_mb:.1f} MB",
                                "memory_bytes": int(mem) if mem.isdigit() else 0,
                                "cmd": cmd[:100]
                            })
                    except:
                        continue
            
            # 按内存排序
            processes.sort(key=lambda x: x["memory_bytes"], reverse=True)
            self.finished.emit(processes)
        except Exception as e:
            self.finished.emit([])


class ProcessPage(QWidget):
    """进程管理页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("processPage")
        self.processes_data = []
        self.auto_refresh = False
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.SPEED_HIGH))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("进程管理"))
        title_layout.addStretch()
        
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索进程...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_table)
        title_layout.addWidget(self.search_edit)
        
        self.auto_checkbox = CheckBox("自动刷新")
        self.auto_checkbox.stateChanged.connect(self._toggle_auto_refresh)
        title_layout.addWidget(self.auto_checkbox)
        
        refresh_btn = PrimaryPushButton("刷新")
        refresh_btn.clicked.connect(self._load_processes)
        title_layout.addWidget(refresh_btn)
        layout.addLayout(title_layout)
        
        # 操作栏
        action_card = CardWidget()
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(20, 15, 20, 15)
        
        kill_btn = PushButton("结束进程")
        kill_btn.clicked.connect(self._kill_selected)
        action_layout.addWidget(kill_btn)
        
        kill_tree_btn = PushButton("结束进程树")
        kill_tree_btn.clicked.connect(self._kill_tree)
        action_layout.addWidget(kill_tree_btn)
        
        open_location_btn = PushButton("打开文件位置")
        open_location_btn.clicked.connect(self._open_location)
        action_layout.addWidget(open_location_btn)
        
        action_layout.addStretch()
        
        self.count_label = BodyLabel("进程数: 0")
        action_layout.addWidget(self.count_label)
        layout.addWidget(action_card)

        # 进程列表
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["进程名", "PID", "内存", "命令行"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        # 自动刷新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._load_processes)
        
        # 初始加载
        self._load_processes()
    
    def _load_processes(self):
        """加载进程列表"""
        self.process_thread = ProcessThread()
        self.process_thread.finished.connect(self._on_load_finished)
        self.process_thread.start()
    
    def _on_load_finished(self, processes):
        """加载完成"""
        self.processes_data = processes
        self._update_table(processes)
        self.count_label.setText(f"进程数: {len(processes)}")
    
    def _update_table(self, processes):
        """更新表格"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(processes))
        for i, p in enumerate(processes):
            self.table.setItem(i, 0, QTableWidgetItem(p["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(p["pid"]))
            
            mem_item = QTableWidgetItem(p["memory"])
            mem_item.setData(Qt.UserRole, p["memory_bytes"])
            self.table.setItem(i, 2, mem_item)
            
            self.table.setItem(i, 3, QTableWidgetItem(p["cmd"]))
        self.table.setSortingEnabled(True)
    
    def _filter_table(self, text):
        """过滤表格"""
        text = text.lower().strip()
        if not text:
            self._update_table(self.processes_data)
            return
        filtered = [p for p in self.processes_data if text in p["name"].lower()]
        self._update_table(filtered)
    
    def _toggle_auto_refresh(self, state):
        """切换自动刷新"""
        if state == Qt.Checked:
            self.timer.start(3000)  # 3秒刷新
        else:
            self.timer.stop()

    
    def _get_selected_pid(self):
        """获取选中的 PID"""
        row = self.table.currentRow()
        if row < 0:
            return None, None
        return self.table.item(row, 1).text(), self.table.item(row, 0).text()
    
    def _kill_selected(self):
        """结束选中进程"""
        pid, name = self._get_selected_pid()
        if not pid:
            InfoBar.warning("提示", "请先选择一个进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        try:
            result = subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                InfoBar.success("成功", f"已结束 {name} (PID: {pid})", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
                self._load_processes()
            else:
                InfoBar.error("失败", result.stderr or "无法结束进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        except Exception as e:
            InfoBar.error("错误", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _kill_tree(self):
        """结束进程树"""
        pid, name = self._get_selected_pid()
        if not pid:
            InfoBar.warning("提示", "请先选择一个进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        try:
            result = subprocess.run(f"taskkill /PID {pid} /T /F", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                InfoBar.success("成功", f"已结束 {name} 及其子进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
                self._load_processes()
            else:
                InfoBar.error("失败", result.stderr or "无法结束进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        except Exception as e:
            InfoBar.error("错误", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
    
    def _open_location(self):
        """打开文件位置"""
        pid, name = self._get_selected_pid()
        if not pid:
            InfoBar.warning("提示", "请先选择一个进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        try:
            result = subprocess.run(
                f'wmic process where ProcessId={pid} get ExecutablePath /format:csv',
                shell=True, capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ',' in line:
                    path = line.split(',')[-1].strip()
                    if path and os.path.exists(path):
                        subprocess.Popen(f'explorer /select,"{path}"')
                        return
            InfoBar.warning("提示", "无法获取文件路径", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
        except Exception as e:
            InfoBar.error("错误", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
