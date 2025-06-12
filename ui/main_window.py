from file import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui
import open3d as o3d
import numpy as np

from .point_tab import PointTabHandler
from .mesh_tab import MeshTabHandler
from .visualization import VisualizationManager
from core.data_manager import DataManager
from core.camera_manager import CameraManager
from core.task_manager import TaskManager
from core.app_context import app_context

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.center_window()
        self.setup_background()
        
        # 初始化管理器
        self.data_manager = DataManager()
        self.camera_manager = CameraManager()
        self.task_manager = TaskManager(self)
        self.visualization_manager = VisualizationManager(self)
        
        # 设置应用上下文
        app_context.setup(self)
        
        # 初始化Tab处理器
        self.point_tab = PointTabHandler()
        self.mesh_tab = MeshTabHandler()
        
        # 绑定基本事件
        self.setup_basic_events()
        
        # 设置定时器
        self.setup_timer()
        
        # 初始化一些全局变量
        self.work_dir = './work/'
        self.normal_color = [0.1, 0.5, 0.9]
        self.selected_color = [1, 0, 0]
        self.fx = 1302.39546
        self.fy = 1301.80638
        self.cx = 689.52858
        self.cy = 504.24215
        self.width = 1280
        self.height = 1024
        self.intrinsic = np.array([[self.fx,0,self.cx],[0,self.fy,self.cy],[0,0,1]])
    
    def setup_background(self):
        self.bg = QtGui.QPixmap()
        self.bg.load('./utils/images/bg1.png')
        self.bg = self.bg.scaled(1920 * 2, 1080 * 2)
        self.setMaximumSize(1920 * 2, 1080 * 2)
    
    def setup_basic_events(self):
        self.ImportButton.clicked.connect(self.data_manager.load_dataset)
        self.tabWidget.currentChanged.connect(self.tab_changed)
    
    def setup_timer(self):
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.visualization_manager.draw_update)
        self.clock.start(20)
    
    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        center_point = screen.center() - window.center()
        self.move(center_point.x(), center_point.y())
    
    def tab_changed(self):
        pass
    
    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.drawPixmap(0, 0, self.bg)