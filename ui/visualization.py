import open3d as o3d
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QWindow
from utils import *
import numpy as np

class VisualizationManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_visualizers()
        self.setup_mouse_callbacks()
        self.setup_keyboard_callbacks()
        
        # 鼠标交互相关
        self.prior_mouse_position = None
        self.is_view_rotating = False
        self.is_translating = False
        self.is_camera_rotating = False
        self.pixel_to_rotate_scale_factor = 0.5
        self.pixel_to_translate_scale_factor = 1
    
    def setup_visualizers(self):
        """设置可视化窗口"""
        # vis1 - 点云窗口
        self.main_window.vis1 = o3d.visualization.VisualizerWithKeyCallback()
        self.main_window.vis1.create_window(visible=False)
        render_opt = self.main_window.vis1.get_render_option()
        render_opt.background_color = [0.6, 0.6, 0.6]
        
        # vis2 - 网格窗口
        self.main_window.vis2 = o3d.visualization.VisualizerWithKeyCallback()
        self.main_window.vis2.create_window(visible=False)
        render_opt = self.main_window.vis2.get_render_option()
        render_opt.background_color = [0.6, 0.6, 0.6]
        
        # 获取窗口ID并嵌入到Qt窗口中
        window_ids = self.find_glfw_window()
        if len(window_ids) >= 2:
            id1, id2 = window_ids[0], window_ids[1]
            
            # 设置点云窗口
            self.sub_window1 = QWindow.fromWinId(id1)
            self.displayer1 = QWidget.createWindowContainer(self.sub_window1)
            layout1 = QVBoxLayout(self.main_window.PointWidget)
            layout1.setContentsMargins(0, 0, 0, 0)
            layout1.addWidget(self.displayer1)
            self.main_window.PointWidget.setLayout(layout1)
            
            # 设置网格窗口
            self.sub_window2 = QWindow.fromWinId(id2)
            self.displayer2 = QWidget.createWindowContainer(self.sub_window2)
            layout2 = QVBoxLayout(self.main_window.meshwidget)
            layout2.setContentsMargins(0, 0, 0, 0)
            layout2.addWidget(self.displayer2)
            self.main_window.meshwidget.setLayout(layout2)
    
    def setup_mouse_callbacks(self):
        """设置鼠标回调"""
        self.main_window.vis1.register_mouse_button_callback(self.on_mouse_button)
        self.main_window.vis1.register_mouse_move_callback(self.on_mouse_move)
    
    def setup_keyboard_callbacks(self):
        """设置键盘回调"""
        vis2 = self.main_window.vis2
        vis2.register_key_callback(ord("W"), self.move_camera_forward)
        vis2.register_key_callback(ord("S"), self.move_camera_backward)
        vis2.register_key_callback(ord("A"), self.move_camera_left)
        vis2.register_key_callback(ord("D"), self.move_camera_right)
        vis2.register_key_callback(ord("Q"), self.move_camera_up)
        vis2.register_key_callback(ord("E"), self.move_camera_down)
    
    def draw_update(self):
        """更新渲染"""
        self.main_window.vis1.poll_events()
        self.main_window.vis1.update_renderer()
        self.main_window.vis2.poll_events()
        self.main_window.vis2.update_renderer()
    
    def find_glfw_window(self):
        """查找GLFW窗口ID"""
        import Xlib
        from Xlib.display import Display
        
        display = Display()
        root = display.screen().root
        window_ids = []
        
        def get_windows(window):
            children = window.query_tree().children
            for child in children:
                try:
                    window_name = child.get_wm_name()
                    if window_name and "Open3D" in window_name:
                        window_ids.append(child.id)
                except Xlib.error.BadWindow:
                    continue
                get_windows(child)
        
        get_windows(root)
        display.close()
        return window_ids
    
    # 相机移动回调
    def move_camera_forward(self, vis):
        view_control = vis.get_view_control()
        view_control.camera_local_translate(forward=1, right=0, up=0)
    
    def move_camera_backward(self, vis):
        view_control = vis.get_view_control()
        view_control.camera_local_translate(forward=-1, right=0, up=0)
    
    def move_camera_left(self, vis):
        view_control = vis.get_view_control()
        view_control.camera_local_translate(forward=0, right=-0.2, up=0)
    
    def move_camera_right(self, vis):
        view_control = vis.get_view_control()
        view_control.camera_local_translate(forward=0, right=0.2, up=0)
    
    def move_camera_up(self, vis):
        view_control = vis.get_view_control()
        view_control.camera_local_translate(forward=0, right=0, up=0.2)
    
    def move_camera_down(self, vis):
        view_control = vis.get_view_control()
        view_control.camera_local_translate(forward=0, right=0, up=-0.2)
    
    # 鼠标交互回调
    def on_mouse_button(self, vis, button, action, mods):
        buttons = ["left", "right", "middle"]
        actions = ["up", "down"]
        mods_name = ["shift", "ctrl", "alt", "cmd"]
        
        button = buttons[button]
        action = actions[action]
        mods = [mods_name[i] for i in range(4) if mods & (1 << i)]
        
        if button == "left" and action == "down" and mods == []:
            self.is_view_rotating = True
        if button == "left" and action == "up":
            self.is_view_rotating = False
        if button == "left" and action == "down" and mods == ["ctrl"]:
            self.is_translating = True
        if button == "left" and action == "up":
            self.is_translating = False
        if button == "left" and action == "down" and mods == ["shift"]:
            self.is_camera_rotating = True
        if button == "left" and action == "up":
            self.is_camera_rotating = False
        if button == "right" and action == "down" and mods == []:
            self.pick_camera(vis, self.prior_mouse_position[0], self.prior_mouse_position[1])
    
    def on_mouse_move(self, vis, x, y):
        if self.prior_mouse_position is not None:
            dx = x - self.prior_mouse_position[0]
            dy = y - self.prior_mouse_position[1]
            view_control = vis.get_view_control()
            
            if self.is_view_rotating:
                view_control.rotate(
                    dx * self.pixel_to_rotate_scale_factor, 
                    dy * self.pixel_to_rotate_scale_factor
                )
            elif self.is_translating:
                view_control.translate(
                    dx * self.pixel_to_translate_scale_factor,
                    dy * self.pixel_to_translate_scale_factor,
                )
            elif self.is_camera_rotating:
                view_control.camera_local_rotate(
                    dx * self.pixel_to_translate_scale_factor,
                    dy * self.pixel_to_translate_scale_factor,
                )
        
        self.prior_mouse_position = (x, y)
    
    def pick_camera(self, vis, x, y):
        """相机拾取功能"""
        from core.app_context import app_context
        
        view_control = vis.get_view_control()
        camera_params = view_control.convert_to_pinhole_camera_parameters()
        intrinsic = camera_params.intrinsic.intrinsic_matrix
        extrinsic = camera_params.extrinsic
        
        # 创建射线
        ray_camera = np.array([
            (x - intrinsic[0, 2]) / intrinsic[0, 0],
            (y - intrinsic[1, 2]) / intrinsic[1, 1],
            1.0,
        ])
        
        ray_camera = ray_camera / np.linalg.norm(ray_camera)
        
        # 转换到世界坐标系
        rotation = extrinsic[:3, :3]
        translation = extrinsic[:3, 3]
        ray_world = np.dot(rotation.T, ray_camera)
        ray_dir = ray_world / np.linalg.norm(ray_world)
        camera_pos = -np.dot(rotation.T, translation)
        
        # 检测相机碰撞
        closest_camera_lookup = {}
        poselist = app_context.camera_manager.poselist
        
        for camera_id, camera in enumerate(poselist):
            vertices = np.asarray(camera.points)[:5]
            for i in range(1, 5):
                v0 = vertices[0]
                v1 = vertices[i]
                v2 = vertices[(i+1)//4]
                hit, intersect_point = ray_triangle_intersect(camera_pos, ray_dir, v0, v1, v2)
                if hit:
                    intersection_distance = np.linalg.norm(intersect_point - camera_pos)
                    closest_camera_lookup[camera_id] = min(
                        intersection_distance, closest_camera_lookup.get(camera_id, np.inf)
                    )
        
        if len(closest_camera_lookup) == 0:
            print("No hit camera")
            return
        
        selected_camera = app_context.get_point_pose_index()
        click_camera_id = min(closest_camera_lookup, key=closest_camera_lookup.get) + 1
        print(f"Click camera: {click_camera_id}")
        
        if click_camera_id != selected_camera:
            app_context.main_window.point_tab.pointindexlast = selected_camera
            app_context.main_window.PointPoseIndex.setValue(click_camera_id)
        if click_camera_id == selected_camera:
            app_context.main_window.point_tab.show_point_pose()