from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from dialogs.point_image_dialog import PointImageDialog
from core.app_context import app_context
import numpy as np
import open3d as o3d
from core import *
import cv2

class PointTabHandler:
    def __init__(self):
        self.setup_events()
        
        # 点云相关属性
        self.pointindexlast = 1
        self.pointcloud = None
        self.pointcloud_down = None
        self.pointcloud_down_project = None
        self.labels = []
        
    def setup_events(self):
        """绑定点云Tab相关事件"""
        main_window = app_context.main_window
        main_window.PointPoseIndex.valueChanged.connect(self.point_index_changed)
        main_window.PointPoseShowButton.clicked.connect(self.show_point_pose)
        main_window.PointProjectButton.clicked.connect(self.point_project)
        main_window.PointUnprojectButton.clicked.connect(self.point_unproject)
        main_window.CheckPointPose.stateChanged.connect(self.check_point_pose)
        main_window.CheckSelectPose.stateChanged.connect(self.check_select_pose)
        main_window.PointButton.clicked.connect(self.point_filter)
    
    def point_index_changed(self, value):
        """处理点云索引变化"""
        app_context.camera_manager.update_camera_color(
            self.pointindexlast - 1, 
            value - 1, 
            app_context.get_vis1()
        )
        self.pointindexlast = value
    
    def show_point_pose(self):
        """显示点云位姿对应的图像"""
        index = app_context.get_point_pose_index()
        image_path = f"{app_context.get_root_path()}imgs_{index}.jpg"
        
        # 检查是否已有相同图像的对话框
        main_window = app_context.main_window
        for dialog in main_window.findChildren(PointImageDialog):
            if hasattr(dialog, 'current_image_path') and dialog.current_image_path == image_path:
                dialog.activateWindow()
                dialog.raise_()
                return
        
        # 限制对话框数量
        if len(main_window.findChildren(PointImageDialog)) == 2:
            return
        
        if image_path:
            dialog = PointImageDialog(main_window)
            dialog.current_image_path = image_path
            dialog.current_image_index = index
            dialog.display_image(image_path)
            dialog.show()
    
    def point_project(self):
        """点云投影到图像"""
        vis1 = app_context.get_vis1()
        view_params = vis1.get_view_control().convert_to_pinhole_camera_parameters()
        
        index = app_context.get_point_pose_index()
        image_path = f"{app_context.get_root_path()}imgs_{index}.jpg"
        traj = app_context.get_trajectory()
        w2c = traj.parameters[index-1].extrinsic
        
        # 读取图像
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 投影逻辑
        projected_pcd = self._project_points_to_image(image, w2c)
        
        # 更新可视化
        vis1.remove_geometry(self.pointcloud_down)
        vis1.add_geometry(projected_pcd)
        vis1.update_geometry(projected_pcd)
        self.pointcloud_down_project = projected_pcd
        
        vis1.get_view_control().convert_from_pinhole_camera_parameters(view_params)
    
    def point_unproject(self):
        """取消点云投影"""
        vis1 = app_context.get_vis1()
        view_params = vis1.get_view_control().convert_to_pinhole_camera_parameters()
        
        vis1.remove_geometry(self.pointcloud_down_project)
        vis1.add_geometry(self.pointcloud_down)
        
        render_opt = vis1.get_render_option()
        render_opt.point_size = 0.2
        vis1.update_geometry(self.pointcloud_down)
        vis1.get_view_control().convert_from_pinhole_camera_parameters(view_params)
    
    def check_point_pose(self, state):
        """切换位姿显示"""
        vis1 = app_context.get_vis1()
        view_params = vis1.get_view_control().convert_to_pinhole_camera_parameters()
        
        poselist = app_context.camera_manager.poselist
        if state == 2:
            for pose in poselist:
                vis1.add_geometry(pose)
        else:
            for pose in poselist:
                vis1.remove_geometry(pose)
        
        vis1.get_view_control().convert_from_pinhole_camera_parameters(view_params)
    
    def check_select_pose(self, state):
        """处理选择位姿状态变化"""
        if app_context.get_root_path() is None:
            return
    
    def point_filter(self):
        """点云滤波"""
        if app_context.task_manager.start_task("点云滤波"):
            points_np = np.asarray(self.pointcloud.points)
            data_dict = {"pcd": points_np}
            
            app_context.task_manager.start_process(
                pointfilter,
                data_dict,
                self._on_point_filter_complete
            )
    
    def _project_points_to_image(self, image, w2c):
        """投影点云到图像的具体实现"""
        main_window = app_context.main_window
        width = main_window.width
        height = main_window.height
        intrinsic = main_window.intrinsic
        
        numpy_points = np.asarray(self.pointcloud_down.points)
        p_w = np.concatenate([numpy_points, np.ones([numpy_points.shape[0], 1])], axis=1)
        p_c = (w2c @ p_w.T).T
        p_c = p_c[:, :3]
        
        # 筛选出在相机前方的点
        mask = p_c[:, 2] > 0
        
        # 归一化并投影到图像平面
        p_c_visible = p_c[mask]
        p_c_normalized = p_c_visible / p_c_visible[:, 2:3]
        p_n = (intrinsic @ p_c_normalized.T).T
        p_n = np.floor(p_n)[:, :2].astype(int)
        
        # 筛选在图像范围内的可见点
        valid_mask = (p_n[:, 0] < width) & (p_n[:, 0] >= 0) & (p_n[:, 1] < height) & (p_n[:, 1] >= 0)
        p_n_valid = p_n[valid_mask]
        
        # 初始化颜色数组
        colors = np.zeros((len(numpy_points), 3))
        fixed_color = [0.5, 0.5, 0.5]
        
        # 为可见点赋图像颜色
        visible_indices = np.where(mask)[0][valid_mask]
        colors[visible_indices] = image[p_n_valid[:, 1], p_n_valid[:, 0]] / 255.0
        
        # 为不可见点赋固定颜色
        invisible_mask = np.ones(len(numpy_points), dtype=bool)
        invisible_mask[visible_indices] = False
        colors[invisible_mask] = fixed_color
        
        # 创建Open3D点云
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(numpy_points)
        pcd.colors = o3d.utility.Vector3dVector(colors)
        
        return pcd
    
    def _on_point_filter_complete(self, result):
        """点云滤波完成回调"""
        pcd = self.pointcloud
        
        for i in range(len(result)):
            if result[i] == -1:
                pcd.colors[i] = [1, 0, 0]
        
        self.labels = result
        vis1 = app_context.get_vis1()
        vis1.clear_geometries()
        vis1.add_geometry(pcd)
        vis1.update_geometry(pcd)
        
        QMessageBox.information(app_context.main_window, "任务完成", "点云滤波完成")