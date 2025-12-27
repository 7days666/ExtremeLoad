"""端口占用查看页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, LineEdit, PrimaryPushButton, SearchLineEdit
)
import subprocess
import re


class ScanThread(QThread):
    """扫描端口线程"""
    finished = pyqtSignal(list)
    
    def run(self):
        try:
            result = subprocess.run("netstat -ano", shell=True, capture_output=True, text=True, timeout=30)
            lines = result.stdout.strip().split('\n')
            ports = []
            for line in lines[4:]:  # 跳过头部
                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0]
                    local = parts[1]
                    foreign = parts[2]
                    state = parts[3] if len(parts) > 4 else ""
                    pid = parts[-1]
                    
                    # 获取进程名
                    proc_name = self._get_process_name(pid)
                    
                    # 解析端口
                    if ':' in local:
                        port = local.rsplit(':', 1)[-1]
                        ports.append({
                            "proto": proto,
                            "local": local,
                            "foreign": foreign,
                            "state": state,
                            "pid": pid,
                            "process": proc_name,
                            "port": port
                        })
            self.finished.emit(ports)
        except Exception as e:
            self.finished.emit([])
    
    def _get_process_name(self, pid):
        try:
            result = subprocess.run(f'tasklist /FI "PID eq {pid}" /FO CSV /NH', 
                                    shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout.strip():
                return result.stdout.strip().split(',')[0].strip('"')
        except:
            pass
        return "未知"


class PortPage(QWidget):
    """端口占用查看页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("portPage")
        self.ports_data = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(IconWidget(FIF.WIFI))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("端口占用查看"))
        title_layout.addStretch()
        
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索端口或进程...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_table)
        title_layout.addWidget(self.search_edit)
        
        refresh_btn = PrimaryPushButton("刷新")
        refresh_btn.clicked.connect(self._scan_ports)
        title_layout.addWidget(refresh_btn)
        layout.addLayout(title_layout)
        
        # 快捷查询
        quick_card = CardWidget()
        quick_layout = QHBoxLayout(quick_card)
        quick_layout.setContentsMargins(20, 15, 20, 15)
        quick_layout.addWidget(BodyLabel("快捷查询:"))
        
        for port in ["80", "443", "3306", "6379", "8080", "3000", "5000"]:
            btn = PushButton(port)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked, p=port: self._quick_search(p))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        layout.addWidget(quick_card)
        
        # 端口查询
        query_card = CardWidget()
        query_layout = QHBoxLayout(query_card)
        query_layout.setContentsMargins(20, 15, 20, 15)
        query_layout.addWidget(BodyLabel("查询端口:"))
        self.port_edit = LineEdit()
        self.port_edit.setPlaceholderText("输入端口号")
        self.port_edit.setFixedWidth(120)
        query_layout.addWidget(self.port_edit)
        
        query_btn = PushButton("查询")
        query_btn.clicked.connect(self._query_port)
        query_layout.addWidget(query_btn)
        
        kill_btn = PushButton("结束占用进程")
        kill_btn.clicked.connect(self._kill_selected)
        query_layout.addWidget(kill_btn)
        query_layout.addStretch()
        layout.addWidget(query_card)

        # 端口列表
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["协议", "本地地址", "远程地址", "状态", "PID", "进程名"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # 状态栏
        self.status_label = BodyLabel("点击刷新按钮扫描端口")
        layout.addWidget(self.status_label)
    
    def _scan_ports(self):
        """扫描端口"""
        self.status_label.setText("正在扫描...")
        self.scan_thread = ScanThread()
        self.scan_thread.finished.connect(self._on_scan_finished)
        self.scan_thread.start()
    
    def _on_scan_finished(self, ports):
        """扫描完成"""
        self.ports_data = ports
        self._update_table(ports)
        self.status_label.setText(f"共 {len(ports)} 条记录")
    
    def _update_table(self, ports):
        """更新表格"""
        self.table.setRowCount(len(ports))
        for i, p in enumerate(ports):
            self.table.setItem(i, 0, QTableWidgetItem(p["proto"]))
            self.table.setItem(i, 1, QTableWidgetItem(p["local"]))
            self.table.setItem(i, 2, QTableWidgetItem(p["foreign"]))
            self.table.setItem(i, 3, QTableWidgetItem(p["state"]))
            self.table.setItem(i, 4, QTableWidgetItem(p["pid"]))
            self.table.setItem(i, 5, QTableWidgetItem(p["process"]))
    
    def _filter_table(self, text):
        """过滤表格"""
        text = text.lower().strip()
        if not text:
            self._update_table(self.ports_data)
            return
        filtered = [p for p in self.ports_data if text in p["port"] or text in p["process"].lower()]
        self._update_table(filtered)
    
    def _quick_search(self, port):
        """快捷搜索"""
        self.search_edit.setText(port)
    
    def _query_port(self):
        """查询指定端口"""
        port = self.port_edit.text().strip()
        if port:
            self.search_edit.setText(port)
    
    def _kill_selected(self):
        """结束选中进程"""
        row = self.table.currentRow()
        if row < 0:
            InfoBar.warning("提示", "请先选择一行", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
            return
        
        pid = self.table.item(row, 4).text()
        process = self.table.item(row, 5).text()
        
        try:
            result = subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                InfoBar.success("成功", f"已结束进程 {process} (PID: {pid})", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=2000)
                self._scan_ports()
            else:
                InfoBar.error("失败", result.stderr or "无法结束进程", parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
        except Exception as e:
            InfoBar.error("错误", str(e), parent=self.window(), position=InfoBarPosition.TOP_RIGHT, duration=3000)
