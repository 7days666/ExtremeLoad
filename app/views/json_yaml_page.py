"""JSON/YAML 工具页面"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, PushButton, TitleLabel, BodyLabel, 
    InfoBar, InfoBarPosition, FluentIcon as FIF, 
    IconWidget, PrimaryPushButton, TextEdit, ComboBox, LineEdit
)
import json
import re


class JsonYamlPage(QWidget):
    """JSON/YAML 工具页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("jsonYamlPage")
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
        title_layout.addWidget(IconWidget(FIF.DOCUMENT))
        title_layout.addSpacing(8)
        title_layout.addWidget(TitleLabel("JSON / YAML 工具"))
        title_layout.addStretch()
        content_layout.addLayout(title_layout)

        # JSON 格式化/压缩
        json_card = CardWidget()
        json_layout = QVBoxLayout(json_card)
        json_layout.setContentsMargins(20, 15, 20, 15)
        json_layout.addWidget(TitleLabel("JSON 格式化 / 压缩 / 校验"))
        
        self.json_input = TextEdit()
        self.json_input.setPlaceholderText('输入 JSON，例如：{"name":"test","value":123}')
        self.json_input.setMinimumHeight(120)
        json_layout.addWidget(self.json_input)
        
        json_btn_layout = QHBoxLayout()
        format_btn = PrimaryPushButton("格式化")
        format_btn.clicked.connect(self._format_json)
        json_btn_layout.addWidget(format_btn)
        
        compress_btn = PushButton("压缩")
        compress_btn.clicked.connect(self._compress_json)
        json_btn_layout.addWidget(compress_btn)
        
        validate_btn = PushButton("校验")
        validate_btn.clicked.connect(self._validate_json)
        json_btn_layout.addWidget(validate_btn)
        
        copy_json_btn = PushButton("复制结果")
        copy_json_btn.clicked.connect(lambda: self._copy_text(self.json_output.toPlainText()))
        json_btn_layout.addWidget(copy_json_btn)
        
        json_btn_layout.addStretch()
        json_layout.addLayout(json_btn_layout)
        
        self.json_output = TextEdit()
        self.json_output.setReadOnly(True)
        self.json_output.setMinimumHeight(120)
        self.json_output.setPlaceholderText("输出结果...")
        json_layout.addWidget(self.json_output)
        content_layout.addWidget(json_card)

        # JSON ↔ YAML 互转
        convert_card = CardWidget()
        convert_layout = QVBoxLayout(convert_card)
        convert_layout.setContentsMargins(20, 15, 20, 15)
        convert_layout.addWidget(TitleLabel("JSON ↔ YAML 互转"))
        
        convert_input_layout = QHBoxLayout()
        
        # 左侧 JSON
        json_side = QVBoxLayout()
        json_side.addWidget(BodyLabel("JSON"))
        self.convert_json = TextEdit()
        self.convert_json.setPlaceholderText('{"key": "value"}')
        self.convert_json.setMinimumHeight(150)
        json_side.addWidget(self.convert_json)
        convert_input_layout.addLayout(json_side)
        
        # 中间按钮
        btn_side = QVBoxLayout()
        btn_side.addStretch()
        to_yaml_btn = PrimaryPushButton("→ YAML")
        to_yaml_btn.clicked.connect(self._json_to_yaml)
        btn_side.addWidget(to_yaml_btn)
        to_json_btn = PushButton("← JSON")
        to_json_btn.clicked.connect(self._yaml_to_json)
        btn_side.addWidget(to_json_btn)
        btn_side.addStretch()
        convert_input_layout.addLayout(btn_side)
        
        # 右侧 YAML
        yaml_side = QVBoxLayout()
        yaml_side.addWidget(BodyLabel("YAML"))
        self.convert_yaml = TextEdit()
        self.convert_yaml.setPlaceholderText("key: value")
        self.convert_yaml.setMinimumHeight(150)
        yaml_side.addWidget(self.convert_yaml)
        convert_input_layout.addLayout(yaml_side)
        
        convert_layout.addLayout(convert_input_layout)
        content_layout.addWidget(convert_card)

        # JSON Path 查询
        path_card = CardWidget()
        path_layout = QVBoxLayout(path_card)
        path_layout.setContentsMargins(20, 15, 20, 15)
        path_layout.addWidget(TitleLabel("JSON Path 查询"))
        
        path_input_layout = QHBoxLayout()
        path_input_layout.addWidget(BodyLabel("路径:"))
        self.json_path_input = LineEdit()
        self.json_path_input.setPlaceholderText("例如: data.users[0].name 或 data.items[*].id")
        path_input_layout.addWidget(self.json_path_input, 1)
        query_btn = PrimaryPushButton("查询")
        query_btn.clicked.connect(self._query_json_path)
        path_input_layout.addWidget(query_btn)
        path_layout.addLayout(path_input_layout)
        
        self.path_json_input = TextEdit()
        self.path_json_input.setPlaceholderText('输入要查询的 JSON...')
        self.path_json_input.setMinimumHeight(100)
        path_layout.addWidget(self.path_json_input)
        
        self.path_result = TextEdit()
        self.path_result.setReadOnly(True)
        self.path_result.setMaximumHeight(80)
        self.path_result.setPlaceholderText("查询结果...")
        path_layout.addWidget(self.path_result)
        content_layout.addWidget(path_card)

        # JSON 转义/反转义
        escape_card = CardWidget()
        escape_layout = QVBoxLayout(escape_card)
        escape_layout.setContentsMargins(20, 15, 20, 15)
        escape_layout.addWidget(TitleLabel("JSON 转义 / 反转义"))
        
        self.escape_input = TextEdit()
        self.escape_input.setPlaceholderText('输入 JSON 字符串...')
        self.escape_input.setMaximumHeight(80)
        escape_layout.addWidget(self.escape_input)
        
        escape_btn_layout = QHBoxLayout()
        escape_btn = PrimaryPushButton("转义")
        escape_btn.clicked.connect(self._escape_json)
        escape_btn_layout.addWidget(escape_btn)
        unescape_btn = PushButton("反转义")
        unescape_btn.clicked.connect(self._unescape_json)
        escape_btn_layout.addWidget(unescape_btn)
        escape_btn_layout.addStretch()
        escape_layout.addLayout(escape_btn_layout)
        
        self.escape_output = TextEdit()
        self.escape_output.setReadOnly(True)
        self.escape_output.setMaximumHeight(80)
        escape_layout.addWidget(self.escape_output)
        content_layout.addWidget(escape_card)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _format_json(self):
        """格式化 JSON"""
        try:
            text = self.json_input.toPlainText().strip()
            if not text:
                return
            data = json.loads(text)
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            self.json_output.setPlainText(formatted)
            InfoBar.success("成功", "JSON 格式化完成", parent=self, position=InfoBarPosition.TOP)
        except json.JSONDecodeError as e:
            self.json_output.setPlainText(f"JSON 解析错误: {str(e)}")
            InfoBar.error("错误", f"JSON 格式错误: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _compress_json(self):
        """压缩 JSON"""
        try:
            text = self.json_input.toPlainText().strip()
            if not text:
                return
            data = json.loads(text)
            compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.json_output.setPlainText(compressed)
            InfoBar.success("成功", "JSON 压缩完成", parent=self, position=InfoBarPosition.TOP)
        except json.JSONDecodeError as e:
            self.json_output.setPlainText(f"JSON 解析错误: {str(e)}")
            InfoBar.error("错误", f"JSON 格式错误: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _validate_json(self):
        """校验 JSON"""
        try:
            text = self.json_input.toPlainText().strip()
            if not text:
                self.json_output.setPlainText("请输入 JSON")
                return
            data = json.loads(text)
            
            # 统计信息
            def count_elements(obj):
                if isinstance(obj, dict):
                    keys = len(obj)
                    nested = sum(count_elements(v) for v in obj.values())
                    return keys + nested
                elif isinstance(obj, list):
                    return len(obj) + sum(count_elements(item) for item in obj)
                return 0
            
            element_count = count_elements(data)
            data_type = "对象" if isinstance(data, dict) else "数组" if isinstance(data, list) else type(data).__name__
            
            result = f"[OK] JSON 格式正确\n\n"
            result += f"统计信息:\n"
            result += f"  - 类型: {data_type}\n"
            result += f"  - 元素数量: {element_count}\n"
            result += f"  - 字符长度: {len(text)}\n"
            
            if isinstance(data, dict):
                result += f"  - 顶层键: {', '.join(list(data.keys())[:10])}"
                if len(data.keys()) > 10:
                    result += f" ... (共 {len(data.keys())} 个)"
            elif isinstance(data, list):
                result += f"  - 数组长度: {len(data)}"
            
            self.json_output.setPlainText(result)
            InfoBar.success("成功", "JSON 格式正确", parent=self, position=InfoBarPosition.TOP)
        except json.JSONDecodeError as e:
            error_msg = f"[ERROR] JSON 格式错误\n\n"
            error_msg += f"错误位置: 第 {e.lineno} 行, 第 {e.colno} 列\n"
            error_msg += f"错误信息: {e.msg}"
            self.json_output.setPlainText(error_msg)
            InfoBar.error("错误", f"JSON 格式错误", parent=self, position=InfoBarPosition.TOP)
    
    def _json_to_yaml(self):
        """JSON 转 YAML"""
        try:
            text = self.convert_json.toPlainText().strip()
            if not text:
                return
            data = json.loads(text)
            yaml_str = self._dict_to_yaml(data)
            self.convert_yaml.setPlainText(yaml_str)
            InfoBar.success("成功", "转换为 YAML 完成", parent=self, position=InfoBarPosition.TOP)
        except json.JSONDecodeError as e:
            InfoBar.error("错误", f"JSON 格式错误: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _yaml_to_json(self):
        """YAML 转 JSON"""
        try:
            text = self.convert_yaml.toPlainText().strip()
            if not text:
                return
            data = self._yaml_to_dict(text)
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            self.convert_json.setPlainText(json_str)
            InfoBar.success("成功", "转换为 JSON 完成", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("错误", f"YAML 解析错误: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _dict_to_yaml(self, data, indent=0):
        """简单的 dict 转 YAML（不依赖外部库）"""
        lines = []
        prefix = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._dict_to_yaml(value, indent + 1))
                elif isinstance(value, list):
                    lines.append(f"{prefix}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"{prefix}  -")
                            for k, v in item.items():
                                if isinstance(v, (dict, list)):
                                    lines.append(f"{prefix}    {k}:")
                                    lines.append(self._dict_to_yaml(v, indent + 3))
                                else:
                                    lines.append(f"{prefix}    {k}: {self._yaml_value(v)}")
                        else:
                            lines.append(f"{prefix}  - {self._yaml_value(item)}")
                else:
                    lines.append(f"{prefix}{key}: {self._yaml_value(value)}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    lines.append(f"{prefix}-")
                    lines.append(self._dict_to_yaml(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {self._yaml_value(item)}")
        
        return "\n".join(filter(None, lines))
    
    def _yaml_value(self, value):
        """转换 YAML 值"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            if any(c in value for c in [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`']):
                return f'"{value}"'
            return value
        return str(value)
    
    def _yaml_to_dict(self, yaml_str):
        """简单的 YAML 转 dict（支持基本语法）"""
        lines = yaml_str.strip().split('\n')
        return self._parse_yaml_lines(lines, 0)[0]
    
    def _parse_yaml_lines(self, lines, start_indent):
        """解析 YAML 行"""
        result = {}
        i = 0
        current_list = None
        current_key = None
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            indent = len(line) - len(line.lstrip())
            
            if indent < start_indent and start_indent > 0:
                break
            
            if stripped.startswith('- '):
                value = stripped[2:].strip()
                if current_list is None:
                    current_list = []
                if ':' in value and not value.startswith('"'):
                    # 内联对象
                    k, v = value.split(':', 1)
                    current_list.append({k.strip(): self._parse_yaml_value(v.strip())})
                else:
                    current_list.append(self._parse_yaml_value(value))
                if current_key:
                    result[current_key] = current_list
                i += 1
                continue
            
            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                current_key = key
                current_list = None
                
                if value:
                    result[key] = self._parse_yaml_value(value)
                else:
                    # 检查下一行的缩进
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_stripped = next_line.strip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        if next_stripped.startswith('- '):
                            # 数组
                            result[key] = []
                            current_list = result[key]
                        elif next_indent > indent:
                            # 嵌套对象
                            sub_lines = []
                            j = i + 1
                            while j < len(lines):
                                sub_line = lines[j]
                                sub_indent = len(sub_line) - len(sub_line.lstrip())
                                if sub_line.strip() and sub_indent <= indent:
                                    break
                                sub_lines.append(sub_line)
                                j += 1
                            result[key], _ = self._parse_yaml_lines(sub_lines, next_indent)
                            i = j - 1
                        else:
                            result[key] = None
                    else:
                        result[key] = None
            i += 1
        
        return result, i
    
    def _parse_yaml_value(self, value):
        """解析 YAML 值"""
        if value in ('null', '~', ''):
            return None
        if value in ('true', 'True', 'TRUE'):
            return True
        if value in ('false', 'False', 'FALSE'):
            return False
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value
    
    def _query_json_path(self):
        """查询 JSON Path"""
        try:
            text = self.path_json_input.toPlainText().strip()
            path = self.json_path_input.text().strip()
            
            if not text or not path:
                return
            
            data = json.loads(text)
            result = self._resolve_json_path(data, path)
            
            if isinstance(result, (dict, list)):
                self.path_result.setPlainText(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                self.path_result.setPlainText(str(result))
            
            InfoBar.success("成功", "查询完成", parent=self, position=InfoBarPosition.TOP)
        except json.JSONDecodeError as e:
            InfoBar.error("错误", f"JSON 格式错误: {str(e)}", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            self.path_result.setPlainText(f"查询错误: {str(e)}")
            InfoBar.error("错误", f"路径查询失败: {str(e)}", parent=self, position=InfoBarPosition.TOP)
    
    def _resolve_json_path(self, data, path):
        """解析 JSON Path（支持简单语法）"""
        # 支持 data.users[0].name 和 data.items[*].id 语法
        parts = re.split(r'\.(?![^\[]*\])', path)
        current = data
        
        for part in parts:
            if not part:
                continue
            
            # 处理数组索引 如 users[0] 或 items[*]
            match = re.match(r'(\w+)\[([0-9*]+)\]', part)
            if match:
                key, index = match.groups()
                if key:
                    current = current[key]
                
                if index == '*':
                    # 返回所有元素
                    if isinstance(current, list):
                        rest_path = '.'.join(parts[parts.index(part)+1:])
                        if rest_path:
                            return [self._resolve_json_path(item, rest_path) for item in current]
                        return current
                else:
                    current = current[int(index)]
            else:
                current = current[part]
        
        return current
    
    def _escape_json(self):
        """转义 JSON 字符串"""
        text = self.escape_input.toPlainText()
        if not text:
            return
        escaped = json.dumps(text, ensure_ascii=False)
        self.escape_output.setPlainText(escaped)
    
    def _unescape_json(self):
        """反转义 JSON 字符串"""
        text = self.escape_input.toPlainText().strip()
        if not text:
            return
        try:
            # 如果是带引号的字符串
            if text.startswith('"') and text.endswith('"'):
                unescaped = json.loads(text)
            else:
                unescaped = json.loads(f'"{text}"')
            self.escape_output.setPlainText(unescaped)
        except json.JSONDecodeError:
            self.escape_output.setPlainText(text.encode().decode('unicode_escape'))
    
    def _copy_text(self, text):
        """复制文本到剪贴板"""
        if text:
            QApplication.clipboard().setText(text)
            InfoBar.success("成功", "已复制到剪贴板", parent=self, position=InfoBarPosition.TOP)
