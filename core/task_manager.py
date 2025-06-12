from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from multiprocessing import Process, Queue

def _prevent_close(event):
    event.ignore()

class TaskManager:
    def __init__(self, parent):
        self.parent = parent
        self.progress_dialog = None
        self.data_queue = Queue()
        self.result_queue = Queue()
        self.process = None
        self.timer = None
        self.current_callback = None
    
    def start_task(self, task_title="Task", max_progress=100):
        """开始任务UI"""
        if self.progress_dialog is None:
            self.progress_dialog = QProgressDialog(self.parent)
            self.progress_dialog.closeEvent = _prevent_close
            self.progress_dialog.setWindowTitle("处理中...")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.setAutoReset(True)
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.setMinimumDuration(500)
        
        self.progress_dialog.setLabelText(f"正在进行{task_title}")
        self.progress_dialog.setRange(0, max_progress)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()
        return True
    
    def start_process(self, target_func, data_dict, callback, check_interval=1000):
        """启动进程"""
        self.current_callback = callback
        self.process = Process(target=target_func, args=(self.data_queue, self.result_queue))
        self.process.start()
        self.data_queue.put(data_dict)
        
        # 设置定时器检查结果
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(check_interval)
        
        # 开始检查任务完成
        QTimer.singleShot(check_interval, self._check_task_complete)
    
    def _update_progress(self):
        """更新进度"""
        if self.progress_dialog.isVisible():
            if self.progress_dialog.value() < 99:
                self.progress_dialog.setValue(self.progress_dialog.value() + 1)
        else:
            if self.timer:
                self.timer.stop()
                self.timer.deleteLater()
                self.timer = None
    
    def _check_task_complete(self):
        """检查任务是否完成"""
        if not self.result_queue.empty():
            self.progress_dialog.setValue(100)
            result = self.result_queue.get()
            self.progress_dialog.hide()
            
            if self.current_callback:
                self.current_callback(result)
            
            if self.timer:
                self.timer.stop()
                self.timer.deleteLater()
                self.timer = None
        else:
            QTimer.singleShot(1000, self._check_task_complete)