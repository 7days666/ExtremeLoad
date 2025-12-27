"""下载管理器 - 统一下载队列、断点续传"""
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import requests
import os
import time

class DownloadTask(QThread):
    """下载任务"""
    progress = pyqtSignal(str, int, int, int)  # task_id, percent, downloaded, total
    speed_updated = pyqtSignal(str, str)  # task_id, speed
    finished = pyqtSignal(str, bool, str)  # task_id, success, message
    
    def __init__(self, task_id, url, save_path, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.url = url
        self.save_path = save_path
        self._is_paused = False
        self._is_cancelled = False
        self._downloaded = 0
    
    def run(self):
        try:
            save_dir = os.path.dirname(self.save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            # 断点续传：检查已下载的部分
            temp_path = self.save_path + ".tmp"
            if os.path.exists(temp_path):
                self._downloaded = os.path.getsize(temp_path)
                headers["Range"] = f"bytes={self._downloaded}-"
            
            response = requests.get(self.url, stream=True, timeout=120, headers=headers, verify=False, allow_redirects=True)
            
            # 获取总大小
            if response.status_code == 206:  # 断点续传
                content_range = response.headers.get('content-range', '')
                total_size = int(content_range.split('/')[-1]) if '/' in content_range else 0
            else:
                total_size = int(response.headers.get('content-length', 0)) + self._downloaded
                self._downloaded = 0  # 服务器不支持断点续传，重新下载

            mode = 'ab' if os.path.exists(temp_path) and response.status_code == 206 else 'wb'
            last_time = time.time()
            last_downloaded = self._downloaded
            
            with open(temp_path, mode) as f:
                for chunk in response.iter_content(chunk_size=32768):
                    # 暂停检查
                    while self._is_paused and not self._is_cancelled:
                        time.sleep(0.1)
                    
                    if self._is_cancelled:
                        self.finished.emit(self.task_id, False, "已取消")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        self._downloaded += len(chunk)
                        
                        # 计算进度和速度
                        if total_size > 0:
                            percent = int(self._downloaded * 100 / total_size)
                            self.progress.emit(self.task_id, percent, self._downloaded, total_size)
                        
                        # 每秒更新一次速度
                        now = time.time()
                        if now - last_time >= 1:
                            speed = (self._downloaded - last_downloaded) / (now - last_time)
                            if speed > 1024 * 1024:
                                speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
                            else:
                                speed_str = f"{speed / 1024:.1f} KB/s"
                            self.speed_updated.emit(self.task_id, speed_str)
                            last_time = now
                            last_downloaded = self._downloaded
            
            # 下载完成，重命名临时文件
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
            os.rename(temp_path, self.save_path)
            self.finished.emit(self.task_id, True, self.save_path)
            
        except Exception as e:
            self.finished.emit(self.task_id, False, str(e))
    
    def pause(self):
        self._is_paused = True
    
    def resume(self):
        self._is_paused = False
    
    def cancel(self):
        self._is_cancelled = True
        self._is_paused = False


class DownloadManager(QObject):
    """下载管理器"""
    task_added = pyqtSignal(str, str, str)  # task_id, name, url
    task_progress = pyqtSignal(str, int, int, int)  # task_id, percent, downloaded, total
    task_speed = pyqtSignal(str, str)  # task_id, speed
    task_finished = pyqtSignal(str, bool, str)  # task_id, success, message
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self.tasks = {}  # task_id -> DownloadTask
        self.task_info = {}  # task_id -> {name, url, save_path, status}
        self.max_concurrent = 3
        self.queue = []  # 等待队列
    
    def add_task(self, name, url, save_path):
        """添加下载任务"""
        task_id = f"{name}_{int(time.time() * 1000)}"
        self.task_info[task_id] = {
            "name": name, "url": url, "save_path": save_path,
            "status": "waiting", "percent": 0
        }
        self.queue.append(task_id)
        self.task_added.emit(task_id, name, url)
        self._process_queue()
        return task_id
    
    def _process_queue(self):
        """处理下载队列"""
        running = sum(1 for t in self.tasks.values() if t.isRunning())
        while self.queue and running < self.max_concurrent:
            task_id = self.queue.pop(0)
            self._start_task(task_id)
            running += 1
    
    def _start_task(self, task_id):
        """启动下载任务"""
        info = self.task_info.get(task_id)
        if not info:
            return
        
        task = DownloadTask(task_id, info["url"], info["save_path"])
        task.progress.connect(self._on_progress)
        task.speed_updated.connect(self._on_speed)
        task.finished.connect(self._on_finished)
        self.tasks[task_id] = task
        info["status"] = "downloading"
        task.start()
    
    def _on_progress(self, task_id, percent, downloaded, total):
        if task_id in self.task_info:
            self.task_info[task_id]["percent"] = percent
        self.task_progress.emit(task_id, percent, downloaded, total)
    
    def _on_speed(self, task_id, speed):
        self.task_speed.emit(task_id, speed)
    
    def _on_finished(self, task_id, success, message):
        if task_id in self.task_info:
            self.task_info[task_id]["status"] = "completed" if success else "failed"
        self.task_finished.emit(task_id, success, message)
        self._process_queue()
    
    def pause_task(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].pause()
            self.task_info[task_id]["status"] = "paused"
    
    def resume_task(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].resume()
            self.task_info[task_id]["status"] = "downloading"
    
    def cancel_task(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
        if task_id in self.queue:
            self.queue.remove(task_id)
