import sys
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt, QMutex, QMutexLocker # Or PyQt6
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QLabel, QFileDialog, QListWidget, QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView, QGraphicsPixmapItem, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QSizePolicy, QDoubleSpinBox, QSpinBox
from PyQt5.QtWidgets import QComboBox, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5 import QtWidgets
import open3d as o3d
import utils
import numpy as np
import os
# --- Worker Class ---
import sys
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt, QMutex, QMutexLocker # Or PyQt6

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QProgressDialog,
)

import numpy as np
# --- Worker Class ---
class Worker(QObject):
    """
    Worker object to perform tasks in a separate thread.
    Handles multiple distinct tasks sequentially.
    """
    # Signals emitted by the worker
    # taskFinished(task_name, success_bool, message_string)
    pointfilter_result = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.data = None

    @pyqtSlot(dict)
    def set_data(self,data):
        self.data = data

    @pyqtSlot()
    def pointfilter_task(self):
        # Todo: 是否接受滤波结果
        os.nice(10)
        task_name = "pointfilter"
        print(f"{task_name} started in thread:", int(QThread.currentThreadId()))
        labels = None
        pcd = self.data['pcd']
        try: # Use try/finally to ensure _end_task is always called
            labels = np.array(
                    pcd.cluster_dbscan(eps=0.02, min_points=100, print_progress=True))
            time.sleep(30)
        finally:
            self.pointfilter_result.emit(labels)
            print(f"{task_name} finished.")

    @pyqtSlot()
    def template_task(self):        
        task_name = ""
        print(f"{task_name} started in thread:", int(QThread.currentThreadId()))
        success = True
        message = f"{task_name} completed successfully."
        try: # Use try/finally to ensure _end_task is always called
            pass
        finally:
            self.taskFinished.emit(task_name, success, message)
            print(f"{task_name} finished.")