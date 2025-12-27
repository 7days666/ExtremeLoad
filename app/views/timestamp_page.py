"""时间戳工具页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, TextEdit, ComboBox, LineEdit, SpinBox
)
from datetime import datetime, timezone, timedelta
import time


class TimestampPage(QWidget):
    """时间戳工具页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("timestampPage")
        self._init_ui()
        self._start_timer()
    
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
        title_layout.addWidget(IconWidget(FIF.HISTORY))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("时间戳工具"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)

        # 当前时间实时显示
        current_card = CardWidget()
        current_layout = QVBoxLayout(current_card)
        current_layout.setContentsMargins(20, 15, 20, 15)
        
        current_title = QHBoxLayout()
        current_title.addWidget(IconWidget(FIF.UPDATE))
        current_title.addSpacing(8)
        current_title.addWidget(TitleLabel("当前时间"))
        current_title.addStretch()
        current_layout.addLayout(current_title)
        
        time_display_layout = QHBoxLayout()
        
        # 时间戳显示
        ts_layout = QVBoxLayout()
        ts_layout.addWidget(BodyLabel("Unix 时间戳 (秒)"))
        self.current_ts_label = TitleLabel("0")
        self.current_ts_label.setStyleSheet("font-size: 24px; color: #0078d4;")
        ts_layout.addWidget(self.current_ts_label)
        time_display_layout.addLayout(ts_layout)
        
        # 毫秒时间戳
        ts_ms_layout = QVBoxLayout()
        ts_ms_layout.addWidget(BodyLabel("Unix 时间戳 (毫秒)"))
        self.current_ts_ms_label = TitleLabel("0")
        self.current_ts_ms_label.setStyleSheet("font-size: 24px; color: #107c10;")
        ts_ms_layout.addWidget(self.current_ts_ms_label)
        time_display_layout.addLayout(ts_ms_layout)
        
        # 日期时间显示
        dt_layout = QVBoxLayout()
        dt_layout.addWidget(BodyLabel("日期时间"))
        self.current_dt_label = TitleLabel("2024-01-01 00:00:00")
        self.current_dt_label.setStyleSheet("font-size: 24px; color: #ca5010;")
        dt_layout.addWidget(self.current_dt_label)
        time_display_layout.addLayout(dt_layout)
        
        current_layout.addLayout(time_display_layout)
        
        # 复制按钮
        copy_btn_layout = QHBoxLayout()
        copy_ts_btn = PushButton("复制秒级时间戳")
        copy_ts_btn.clicked.connect(lambda: self._copy_text(self.current_ts_label.text()))
        copy_btn_layout.addWidget(copy_ts_btn)
        
        copy_ts_ms_btn = PushButton("复制毫秒时间戳")
        copy_ts_ms_btn.clicked.connect(lambda: self._copy_text(self.current_ts_ms_label.text()))
        copy_btn_layout.addWidget(copy_ts_ms_btn)
        
        copy_dt_btn = PushButton("复制日期时间")
        copy_dt_btn.clicked.connect(lambda: self._copy_text(self.current_dt_label.text()))
        copy_btn_layout.addWidget(copy_dt_btn)
        copy_btn_layout.addStretch()
        current_layout.addLayout(copy_btn_layout)
        content_layout.addWidget(current_card)

        # 时间戳 → 日期时间
        ts_to_dt_card = CardWidget()
        ts_to_dt_layout = QVBoxLayout(ts_to_dt_card)
        ts_to_dt_layout.setContentsMargins(20, 15, 20, 15)
        
        ts_to_dt_title = QHBoxLayout()
        ts_to_dt_title.addWidget(IconWidget(FIF.SYNC))
        ts_to_dt_title.addSpacing(8)
        ts_to_dt_title.addWidget(TitleLabel("时间戳 → 日期时间"))
        ts_to_dt_title.addStretch()
        ts_to_dt_layout.addLayout(ts_to_dt_title)
        
        ts_input_layout = QHBoxLayout()
        ts_input_layout.addWidget(BodyLabel("时间戳:"))
        self.ts_input = LineEdit()
        self.ts_input.setPlaceholderText("输入时间戳，如 1703664000 或 1703664000000")
        ts_input_layout.addWidget(self.ts_input, 1)
        
        self.ts_unit_combo = ComboBox()
        self.ts_unit_combo.addItems(["自动检测", "秒 (s)", "毫秒 (ms)", "微秒 (μs)", "纳秒 (ns)"])
        ts_input_layout.addWidget(self.ts_unit_combo)
        
        ts_to_dt_btn = PrimaryPushButton("转换")
        ts_to_dt_btn.clicked.connect(self._ts_to_datetime)
        ts_input_layout.addWidget(ts_to_dt_btn)
        ts_to_dt_layout.addLayout(ts_input_layout)
        
        self.ts_to_dt_result = TextEdit()
        self.ts_to_dt_result.setReadOnly(True)
        self.ts_to_dt_result.setMaximumHeight(120)
        self.ts_to_dt_result.setPlaceholderText("转换结果...")
        ts_to_dt_layout.addWidget(self.ts_to_dt_result)
        content_layout.addWidget(ts_to_dt_card)

        # 日期时间 → 时间戳
        dt_to_ts_card = CardWidget()
        dt_to_ts_layout = QVBoxLayout(dt_to_ts_card)
        dt_to_ts_layout.setContentsMargins(20, 15, 20, 15)
        
        dt_to_ts_title = QHBoxLayout()
        dt_to_ts_title.addWidget(IconWidget(FIF.SYNC))
        dt_to_ts_title.addSpacing(8)
        dt_to_ts_title.addWidget(TitleLabel("日期时间 → 时间戳"))
        dt_to_ts_title.addStretch()
        dt_to_ts_layout.addLayout(dt_to_ts_title)
        
        dt_input_layout = QHBoxLayout()
        dt_input_layout.addWidget(BodyLabel("日期时间:"))
        self.dt_input = LineEdit()
        self.dt_input.setPlaceholderText("如: 2024-12-27 15:30:00")
        dt_input_layout.addWidget(self.dt_input, 1)
        
        now_btn = PushButton("当前时间")
        now_btn.clicked.connect(lambda: self.dt_input.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        dt_input_layout.addWidget(now_btn)
        
        dt_to_ts_btn = PrimaryPushButton("转换")
        dt_to_ts_btn.clicked.connect(self._datetime_to_ts)
        dt_input_layout.addWidget(dt_to_ts_btn)
        dt_to_ts_layout.addLayout(dt_input_layout)
        
        self.dt_to_ts_result = TextEdit()
        self.dt_to_ts_result.setReadOnly(True)
        self.dt_to_ts_result.setMaximumHeight(100)
        self.dt_to_ts_result.setPlaceholderText("转换结果...")
        dt_to_ts_layout.addWidget(self.dt_to_ts_result)
        content_layout.addWidget(dt_to_ts_card)

        # 时区转换
        tz_card = CardWidget()
        tz_layout = QVBoxLayout(tz_card)
        tz_layout.setContentsMargins(20, 15, 20, 15)
        
        tz_title = QHBoxLayout()
        tz_title.addWidget(IconWidget(FIF.GLOBE))
        tz_title.addSpacing(8)
        tz_title.addWidget(TitleLabel("时区转换"))
        tz_title.addStretch()
        tz_layout.addLayout(tz_title)
        
        tz_input_layout = QHBoxLayout()
        tz_input_layout.addWidget(BodyLabel("日期时间:"))
        self.tz_dt_input = LineEdit()
        self.tz_dt_input.setPlaceholderText("如: 2024-12-27 15:30:00")
        tz_input_layout.addWidget(self.tz_dt_input, 1)
        tz_layout.addLayout(tz_input_layout)
        
        tz_select_layout = QHBoxLayout()
        tz_select_layout.addWidget(BodyLabel("从:"))
        self.from_tz_combo = ComboBox()
        self.from_tz_combo.addItems([
            "UTC+8 (北京/上海)", "UTC+0 (伦敦/UTC)", "UTC-5 (纽约)", 
            "UTC-8 (洛杉矶)", "UTC+9 (东京)", "UTC+5:30 (孟买)",
            "UTC+1 (巴黎)", "UTC+10 (悉尼)"
        ])
        tz_select_layout.addWidget(self.from_tz_combo)
        
        tz_select_layout.addWidget(BodyLabel("到:"))
        self.to_tz_combo = ComboBox()
        self.to_tz_combo.addItems([
            "UTC+0 (伦敦/UTC)", "UTC+8 (北京/上海)", "UTC-5 (纽约)", 
            "UTC-8 (洛杉矶)", "UTC+9 (东京)", "UTC+5:30 (孟买)",
            "UTC+1 (巴黎)", "UTC+10 (悉尼)"
        ])
        tz_select_layout.addWidget(self.to_tz_combo)
        
        tz_convert_btn = PrimaryPushButton("转换")
        tz_convert_btn.clicked.connect(self._convert_timezone)
        tz_select_layout.addWidget(tz_convert_btn)
        tz_layout.addLayout(tz_select_layout)
        
        self.tz_result = TextEdit()
        self.tz_result.setReadOnly(True)
        self.tz_result.setMaximumHeight(80)
        self.tz_result.setPlaceholderText("转换结果...")
        tz_layout.addWidget(self.tz_result)
        content_layout.addWidget(tz_card)

        # 时间差计算
        diff_card = CardWidget()
        diff_layout = QVBoxLayout(diff_card)
        diff_layout.setContentsMargins(20, 15, 20, 15)
        
        diff_title = QHBoxLayout()
        diff_title.addWidget(IconWidget(FIF.REMOVE_FROM))
        diff_title.addSpacing(8)
        diff_title.addWidget(TitleLabel("时间差计算"))
        diff_title.addStretch()
        diff_layout.addLayout(diff_title)
        
        diff_input_layout = QHBoxLayout()
        self.diff_start = LineEdit()
        self.diff_start.setPlaceholderText("开始时间: 2024-12-27 00:00:00")
        diff_input_layout.addWidget(self.diff_start, 1)
        diff_input_layout.addWidget(BodyLabel(" → "))
        self.diff_end = LineEdit()
        self.diff_end.setPlaceholderText("结束时间: 2024-12-28 12:30:00")
        diff_input_layout.addWidget(self.diff_end, 1)
        
        diff_calc_btn = PrimaryPushButton("计算")
        diff_calc_btn.clicked.connect(self._calc_time_diff)
        diff_input_layout.addWidget(diff_calc_btn)
        diff_layout.addLayout(diff_input_layout)
        
        self.diff_result = TextEdit()
        self.diff_result.setReadOnly(True)
        self.diff_result.setMaximumHeight(80)
        self.diff_result.setPlaceholderText("计算结果...")
        diff_layout.addWidget(self.diff_result)
        content_layout.addWidget(diff_card)

        # 常用时间戳
        common_card = CardWidget()
        common_layout = QVBoxLayout(common_card)
        common_layout.setContentsMargins(20, 15, 20, 15)
        
        common_title = QHBoxLayout()
        common_title.addWidget(IconWidget(FIF.CALENDAR))
        common_title.addSpacing(8)
        common_title.addWidget(TitleLabel("常用时间戳"))
        common_title.addStretch()
        common_layout.addLayout(common_title)
        
        common_btn_layout = QHBoxLayout()
        
        today_start_btn = PushButton("今天 00:00:00")
        today_start_btn.clicked.connect(lambda: self._show_common_ts("today_start"))
        common_btn_layout.addWidget(today_start_btn)
        
        today_end_btn = PushButton("今天 23:59:59")
        today_end_btn.clicked.connect(lambda: self._show_common_ts("today_end"))
        common_btn_layout.addWidget(today_end_btn)
        
        week_start_btn = PushButton("本周一")
        week_start_btn.clicked.connect(lambda: self._show_common_ts("week_start"))
        common_btn_layout.addWidget(week_start_btn)
        
        month_start_btn = PushButton("本月1号")
        month_start_btn.clicked.connect(lambda: self._show_common_ts("month_start"))
        common_btn_layout.addWidget(month_start_btn)
        
        year_start_btn = PushButton("今年1月1日")
        year_start_btn.clicked.connect(lambda: self._show_common_ts("year_start"))
        common_btn_layout.addWidget(year_start_btn)
        
        common_layout.addLayout(common_btn_layout)
        
        self.common_result = TextEdit()
        self.common_result.setReadOnly(True)
        self.common_result.setMaximumHeight(60)
        common_layout.addWidget(self.common_result)
        content_layout.addWidget(common_card)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _start_timer(self):
        """启动定时器更新当前时间"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_current_time)
        self.timer.start(100)  # 每100ms更新一次
        self._update_current_time()
    
    def _update_current_time(self):
        """更新当前时间显示"""
        now = datetime.now()
        ts = int(now.timestamp())
        ts_ms = int(now.timestamp() * 1000)
        
        self.current_ts_label.setText(str(ts))
        self.current_ts_ms_label.setText(str(ts_ms))
        self.current_dt_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
    
    def _ts_to_datetime(self):
        """时间戳转日期时间"""
        try:
            ts_str = self.ts_input.text().strip()
            if not ts_str:
                return
            
            ts = int(ts_str)
            unit = self.ts_unit_combo.currentText()
            
            # 自动检测单位
            if "自动" in unit:
                if ts > 1e18:
                    unit = "纳秒"
                elif ts > 1e15:
                    unit = "微秒"
                elif ts > 1e12:
                    unit = "毫秒"
                else:
                    unit = "秒"
            
            # 转换为秒
            if "纳秒" in unit or "ns" in unit:
                ts_sec = ts / 1e9
            elif "微秒" in unit or "μs" in unit:
                ts_sec = ts / 1e6
            elif "毫秒" in unit or "ms" in unit:
                ts_sec = ts / 1e3
            else:
                ts_sec = ts
            
            dt = datetime.fromtimestamp(ts_sec)
            dt_utc = datetime.utcfromtimestamp(ts_sec)
            
            result = f"本地时间 (UTC+8): {dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n"
            result += f"UTC 时间: {dt_utc.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n"
            result += f"星期: {['一', '二', '三', '四', '五', '六', '日'][dt.weekday()]}\n"
            result += f"检测单位: {unit}\n"
            result += f"秒级时间戳: {int(ts_sec)}"
            
            self.ts_to_dt_result.setPlainText(result)
            InfoBar.success("成功", "转换完成", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("错误", f"转换失败: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _datetime_to_ts(self):
        """日期时间转时间戳"""
        try:
            dt_str = self.dt_input.text().strip()
            if not dt_str:
                return
            
            # 尝试多种格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M",
            ]
            
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                raise ValueError("无法解析日期格式")
            
            ts = int(dt.timestamp())
            ts_ms = int(dt.timestamp() * 1000)
            
            result = f"秒级时间戳: {ts}\n"
            result += f"毫秒时间戳: {ts_ms}\n"
            result += f"解析结果: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.dt_to_ts_result.setPlainText(result)
            InfoBar.success("成功", "转换完成", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("错误", f"转换失败: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _convert_timezone(self):
        """时区转换"""
        try:
            dt_str = self.tz_dt_input.text().strip()
            if not dt_str:
                return
            
            # 解析日期时间
            formats = ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M"]
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                raise ValueError("无法解析日期格式")
            
            # 解析时区偏移
            tz_offsets = {
                "UTC+8": 8, "UTC+0": 0, "UTC-5": -5, "UTC-8": -8,
                "UTC+9": 9, "UTC+5:30": 5.5, "UTC+1": 1, "UTC+10": 10
            }
            
            from_tz_text = self.from_tz_combo.currentText()
            to_tz_text = self.to_tz_combo.currentText()
            
            from_offset = None
            to_offset = None
            for key, val in tz_offsets.items():
                if key in from_tz_text:
                    from_offset = val
                if key in to_tz_text:
                    to_offset = val
            
            if from_offset is None or to_offset is None:
                raise ValueError("无法解析时区")
            
            # 计算时差并转换
            diff_hours = to_offset - from_offset
            new_dt = dt + timedelta(hours=diff_hours)
            
            result = f"原时间 ({from_tz_text.split('(')[1].split(')')[0]}): {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result += f"目标时间 ({to_tz_text.split('(')[1].split(')')[0]}): {new_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result += f"时差: {diff_hours:+.1f} 小时"
            
            self.tz_result.setPlainText(result)
            InfoBar.success("成功", "时区转换完成", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("错误", f"转换失败: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _calc_time_diff(self):
        """计算时间差"""
        try:
            start_str = self.diff_start.text().strip()
            end_str = self.diff_end.text().strip()
            
            if not start_str or not end_str:
                return
            
            formats = ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M"]
            
            start_dt = None
            end_dt = None
            
            for fmt in formats:
                try:
                    if start_dt is None:
                        start_dt = datetime.strptime(start_str, fmt)
                except ValueError:
                    pass
                try:
                    if end_dt is None:
                        end_dt = datetime.strptime(end_str, fmt)
                except ValueError:
                    pass
            
            if start_dt is None or end_dt is None:
                raise ValueError("无法解析日期格式")
            
            diff = end_dt - start_dt
            total_seconds = int(diff.total_seconds())
            
            days = diff.days
            hours, remainder = divmod(abs(total_seconds) % 86400, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            sign = "" if total_seconds >= 0 else "-"
            
            result = f"时间差: {sign}{abs(days)} 天 {hours} 小时 {minutes} 分 {seconds} 秒\n"
            result += f"总秒数: {total_seconds} 秒\n"
            result += f"总小时: {total_seconds / 3600:.2f} 小时"
            
            self.diff_result.setPlainText(result)
            InfoBar.success("成功", "计算完成", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("错误", f"计算失败: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _show_common_ts(self, time_type):
        """显示常用时间戳"""
        now = datetime.now()
        
        if time_type == "today_start":
            dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
            label = "今天 00:00:00"
        elif time_type == "today_end":
            dt = now.replace(hour=23, minute=59, second=59, microsecond=0)
            label = "今天 23:59:59"
        elif time_type == "week_start":
            dt = now - timedelta(days=now.weekday())
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            label = "本周一 00:00:00"
        elif time_type == "month_start":
            dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            label = "本月1号 00:00:00"
        elif time_type == "year_start":
            dt = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            label = "今年1月1日 00:00:00"
        else:
            return
        
        ts = int(dt.timestamp())
        result = f"{label}: {dt.strftime('%Y-%m-%d %H:%M:%S')} | 时间戳: {ts}"
        self.common_result.setPlainText(result)
        
        # 自动复制到剪贴板
        QApplication.clipboard().setText(str(ts))
        InfoBar.success("成功", f"已复制 {label} 时间戳", parent=self, position=InfoBarPosition.TOP)
    
    def _copy_text(self, text):
        """复制文本到剪贴板"""
        if text:
            QApplication.clipboard().setText(text)
            InfoBar.success("成功", "已复制到剪贴板", parent=self, position=InfoBarPosition.TOP)
