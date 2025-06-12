import os
import utils
import open3d as o3d
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from core.app_context import app_context
from utils import *

class DataManager:

    def __init__(self):

        self.root = None
        self.images = None
        self.pcdfiles = None
        self.selected = []
        self.traj = None
        self.traj_selected = None
        self.pcd_index_list = None
    
    def load_dataset(self):
        """加载数据集"""
        path = QFileDialog.getExistingDirectory(app_context.main_window, '选择文件夹', './work/Data')
        
        if 'PCD' not in path:
            return False
        
        self.root = path + "/"
        self._load_files()
        self._process_keyframes()
        self._generate_trajectory()
        self._load_point_clouds()
        self._setup_ui()
        return True
    
    def _load_files(self):
        """加载文件列表"""
        self.pcdfiles = sort_files_by_number(self.root, 'pcd')
        self.images = sort_files_by_number(self.root, 'jpg')
    
    def _process_keyframes(self):
        """处理关键帧选择"""
        index_notblur = range(len(self.images))
        poses = get_poses(self.root)
        selected = select_keyframes_by_norm(poses, index_notblur, norm_thresh=0.8)
        
        self.selected = [
            list(range(len(self.images))),
            [],
            selected
        ]
        
        write_to_file(self.selected[app_context.get_check_select_pose_state()], './work/index_list.txt')
    
    def _generate_trajectory(self):
        """生成轨迹文件"""
        generate_trajectory_file(self.root, self.root + "traj.log")
        self.traj = o3d.io.read_pinhole_camera_trajectory(self.root + "traj.log")
        self.traj_selected = o3d.io.read_pinhole_camera_trajectory(self.root + "traj.log")
        self.traj_selected.parameters = [
            para for index, para in enumerate(self.traj.parameters) 
            if index in self.selected[app_context.get_check_select_pose_state()]
        ]
    
    def _load_point_clouds(self):
        """加载点云数据"""
        pointcloud = o3d.geometry.PointCloud()
        points = []
        pcd_index_list = []
        
        for index, file_path in enumerate(self.pcdfiles):
            pcd = o3d.io.read_point_cloud(self.root + file_path)
            index_list = np.full(len(pcd.points), index, dtype=int)
            pcd_index_list.append(index_list)
            
            if not pcd.has_points():
                print(f"警告: {file_path} 不包含点数据，跳过")
                continue
            points.append(np.asarray(pcd.points))
        
        self.pcd_index_list = np.hstack(pcd_index_list)
        merged_points = np.vstack(points)
        pointcloud.points = o3d.utility.Vector3dVector(merged_points)
        pointcloud.paint_uniform_color([0.5, 0.5, 0.5])
        
        # 设置到point_tab
        app_context.main_window.point_tab.pointcloud = pointcloud
        app_context.main_window.point_tab.pointcloud_down = pointcloud.random_down_sample(sampling_ratio=0.1)
        app_context.main_window.point_tab.pointcloud_down.paint_uniform_color([0.5, 0.5, 0.5])
        app_context.main_window.point_tab.labels = np.zeros(len(pointcloud.points))
    
    def _setup_ui(self):
        """设置UI"""
        app_context.update_root_label(self.root)
        
        # 设置可视化
        vis1 = app_context.get_vis1()
        vis1.clear_geometries()
        vis1.add_geometry(app_context.main_window.point_tab.pointcloud_down)
        render_opt = vis1.get_render_option()
        render_opt.point_size = 0.2
        vis1.update_geometry(app_context.main_window.point_tab.pointcloud_down)
        
        # 设置相机位姿
        app_context.camera_manager.setup_cameras(self.traj)
        
        # 启用控件
        app_context.set_point_pose_index_enabled(True)
        app_context.set_point_pose_index_maximum(len(self.traj.parameters))
        
        # 清理工作目录
        clear_directory("./work/depth")
        clear_directory("./work/visualdepth")
        
        # 清理CAM文件
        self._clear_cam_files()
    
    def _clear_cam_files(self):
        """清理CAM文件"""
        import glob
        pattern = os.path.join(self.root, '*.CAM')
        for cam_file in glob.glob(pattern):
            try:
                os.remove(cam_file)
            except Exception:
                pass