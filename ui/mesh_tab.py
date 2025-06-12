from PyQt5.QtWidgets import QMessageBox, QFileDialog
from dialogs.mesh_image_dialog import MeshImageDialog
from core.app_context import app_context
import open3d as o3d
from core import *
import os
import glob
from utils import *
import cv2
import numpy as np
class MeshTabHandler:
    def __init__(self):
        self.setup_events()
        
        # 网格相关属性
        self.mesh_path = None
        self.depth_mesh = None
        self.meshindexlast = 1
        
    def setup_events(self):
        """绑定网格Tab相关事件"""
        main_window = app_context.main_window
        main_window.MeshButton.clicked.connect(self.get_mesh)
        main_window.DepthButton.clicked.connect(self.get_depth)
        main_window.MeshSelectButton.clicked.connect(self.select_mesh)
        main_window.MeshColorButton.clicked.connect(self.mvs_texturing)
        main_window.PoseIndex.valueChanged.connect(self.index_changed)
        main_window.PoseShowButton.clicked.connect(self.show_pose)
        main_window.OptimizeButton.clicked.connect(self.optimize)
    
    def get_mesh(self):
        """生成网格"""
        if app_context.get_root_path() is None:
            QMessageBox.warning(app_context.main_window, "警告", "请先导入数据集")
            return
        
        if app_context.task_manager.start_task("网格生成"):
            data_dict = self._prepare_mesh_data()
            app_context.task_manager.start_process(
                get_mesh,
                data_dict,
                self._on_mesh_complete
            )
    
    def get_depth(self):
        """生成深度图"""
        if not self._validate_depth_generation():
            return
        print(app_context.get_root_path())
        print(self.mesh_path)


        if app_context.task_manager.start_task("深度生成"):
            data_dict = {
                "dataset_path": app_context.get_root_path(),
                "mesh_path": self.mesh_path
            }
            app_context.task_manager.start_process(
                get_depth,
                data_dict,
                self._on_depth_complete
            )
    
    def select_mesh(self):
        """选择网格文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            app_context.main_window, "选择网格文件", "./work/Data/", "PLY Files (*.ply)"
        )
        
        if file_path:
            self._load_mesh_file(file_path)
    
    def mvs_texturing(self):
        """MVS纹理化"""
        if not self._validate_texturing():
            return
        
        if app_context.task_manager.start_task("纹理上色"):
            self._generate_cam_file()
            data_dict = {
                "dataset_path": app_context.get_root_path(),
                "mesh_path": self.mesh_path,
                "target_dir": "./work/meshobj/"
            }
            app_context.task_manager.start_process(
                mvstexturing,
                data_dict,
                self._on_texturing_complete
            )
    
    def optimize(self):
        """位姿优化"""
        if not self._validate_optimization():
            return
        
        if app_context.task_manager.start_task("位姿优化"):
            data_dict = self._prepare_optimization_data()
            app_context.task_manager.start_process(
                optimize,
                data_dict,
                self._on_optimization_complete
            )
    
    def index_changed(self, value):
        """处理索引变化"""
        selected_indices = app_context.get_selected_indices(app_context.get_check_select_pose_state())
        app_context.camera_manager.update_camera_color(
            selected_indices[self.meshindexlast - 1],
            selected_indices[value - 1],
            app_context.get_vis2()
        )
        self.meshindexlast = value
    
    def show_pose(self):
        """显示位姿对应的图像"""
        index = app_context.get_pose_index()
        selected_indices = app_context.get_selected_indices(app_context.get_check_select_pose_state())
        image_path = f'./work/blend/imgs_{selected_indices[index-1]+1}.jpg'
        
        if image_path:
            dialog = MeshImageDialog(app_context.main_window)
            dialog.display_image(image_path)
            dialog.exec_()
    
    # 私有辅助方法
    def _prepare_mesh_data(self):
        """准备网格生成数据"""
        return {
            "voxelsize": app_context.get_voxel_size(),
            "trunction": app_context.get_trunction(),
            "minweight": app_context.get_min_weight(),
            "component": app_context.get_component(),
            "iteration": app_context.get_iteration(),
            "traj_file": app_context.get_root_path() + 'traj.log',
            "dataset_path": app_context.get_root_path(),
            "pcdfiles": app_context.get_pcd_files(),
            "labels": app_context.main_window.point_tab.labels
        }
    
    def _prepare_optimization_data(self):
        """准备优化数据"""
        return {
            "directory_depth": app_context.main_window.work_dir + "depth/",
            "directory_color": app_context.get_root_path(),
            "color_paths": app_context.get_images(),
            "selected": app_context.data_manager.selected,
            "checkselect": app_context.get_check_select_pose_state(),
            "dataset_path": app_context.get_root_path(),
            "mesh_path": self.mesh_path,
            "coloriteration": app_context.get_color_iteration()
        }
    
    def _validate_depth_generation(self):
        """验证深度生成条件"""
        if app_context.get_root_path() is None:
            QMessageBox.information(app_context.main_window, "提示", "请先导入数据集")
            return False
        elif self.mesh_path is None:
            QMessageBox.information(app_context.main_window, "提示", "请先导入或生成网格")
            return False
        return True
    
    def _validate_texturing(self):
        """验证纹理化条件"""
        if app_context.get_root_path() is None:
            QMessageBox.information(app_context.main_window, "提示", "请先导入数据集")
            return False
        elif self.mesh_path is None:
            QMessageBox.information(app_context.main_window, "提示", "请先导入或生成网格")
            return False
        return True
    
    def _validate_optimization(self):
        """验证优化条件"""
        path = self.mesh_path
        mesh_prefix = os.path.dirname(path) + "/"
        if mesh_prefix != app_context.get_root_path():
            QMessageBox.information(app_context.main_window, "提示", "数据集与网格匹配失败！")
            return False
        elif self.depth_mesh != self.mesh_path:
            QMessageBox.information(app_context.main_window, "提示", "深度图与网格匹配失败，请重新生成深度！")
            return False
        return True
    
    def _load_mesh_file(self, file_path):
        """加载网格文件"""
        vis2 = app_context.get_vis2()
        view_params = vis2.get_view_control().convert_to_pinhole_camera_parameters()
        
        path = file_path.split("/")[-1]
        app_context.update_mesh_path(path)
        self.mesh_path = file_path
        
        mesh_out = o3d.io.read_triangle_mesh(file_path)
        mesh_out.compute_vertex_normals()
        vis2.clear_geometries()
        vis2.add_geometry(mesh_out)
        vis2.update_geometry(mesh_out)
        vis2.get_view_control().convert_from_pinhole_camera_parameters(view_params)
    
    def _generate_cam_file(self):
        """生成CAM文件"""
        selected_indices = app_context.get_selected_indices(app_context.get_check_select_pose_state())
        traj = app_context.get_trajectory()
        root_path = app_context.get_root_path()
        main_window = app_context.main_window
        
        for index, value in enumerate(selected_indices):
            cam_filename = root_path + f'imgs_{value+1}.CAM'
            with open(cam_filename, 'w') as cam_file:
                extrinsic = traj.parameters[value].extrinsic
                cam_file.write(f"{extrinsic[0,3]} {extrinsic[1,3]} {extrinsic[2,3]} ")
                cam_file.write(f"{extrinsic[0,0]} {extrinsic[0,1]} {extrinsic[0,2]} ")
                cam_file.write(f"{extrinsic[1,0]} {extrinsic[1,1]} {extrinsic[1,2]} ")
                cam_file.write(f"{extrinsic[2,0]} {extrinsic[2,1]} {extrinsic[2,2]}")
                cam_file.write("\n")
                cam_file.write(f"{main_window.fx/main_window.width} 0 0 {main_window.fy/main_window.fx} {main_window.cx/main_window.width} {main_window.cy/main_window.height}")
    
    def _blend_rgb_and_depth(self, alpha=0.5):
        """混合RGB和深度图"""
        directory_depth = app_context.main_window.work_dir + "visualdepth/"
        directory_color = app_context.get_root_path()
        depth_paths = sort_files_by_number(directory_depth, 'png')
        color_paths = sort_files_by_number(directory_color, 'jpg')
        selected_indices = app_context.get_selected_indices(app_context.get_check_select_pose_state())
        
        for i in range(len(depth_paths)):
            rgb_image = cv2.imread(directory_color + color_paths[selected_indices[i]], cv2.IMREAD_COLOR)
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
            
            depth_image = cv2.imread(directory_depth + depth_paths[i], cv2.IMREAD_UNCHANGED)
            depth_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
            depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_JET)
            
            blended_image = cv2.addWeighted(rgb_image, alpha, depth_colored, 1 - alpha, 0)
            cv2.imwrite("./work/blend/" + color_paths[selected_indices[i]], cv2.cvtColor(blended_image, cv2.COLOR_RGB2BGR))
    
    # 回调方法
    def _on_mesh_complete(self, result):
        """网格生成完成回调"""
        mesh_out = o3d.io.read_triangle_mesh(result)
        mesh_out.compute_vertex_normals()
        
        vis2 = app_context.get_vis2()
        vis2.clear_geometries()
        vis2.add_geometry(mesh_out)
        vis2.update_geometry(mesh_out)
        
        path = result.split("/")[-1]
        app_context.update_mesh_path(path)
        self.mesh_path = result
        
        QMessageBox.information(app_context.main_window, "任务完成", "网格生成完成")
    
    def _on_depth_complete(self, result):
        """深度生成完成回调"""
        self.depth_mesh = self.mesh_path
        self._blend_rgb_and_depth()
        QMessageBox.information(app_context.main_window, "任务完成", "深度生成完成")
    
    def _on_texturing_complete(self, result):
        """纹理化完成回调"""
        mesh = o3d.io.read_triangle_mesh(result, enable_post_processing=True, print_progress=True)
        
        vis2 = app_context.get_vis2()
        view_params = vis2.get_view_control().convert_to_pinhole_camera_parameters()
        vis2.clear_geometries()
        vis2.add_geometry(mesh)
        vis2.update_geometry(mesh)
        vis2.get_view_control().convert_from_pinhole_camera_parameters(view_params)
        
        QMessageBox.information(app_context.main_window, "任务完成", "纹理上色完成")
    
    def _on_optimization_complete(self, result):
        """优化完成回调"""
        mesh = o3d.io.read_triangle_mesh(result)
        vis2 = app_context.get_vis2()
        vis2.clear_geometries()
        vis2.add_geometry(mesh)
        vis2.update_geometry(mesh)
        
        # 添加相机位姿显示
        selected_indices = app_context.get_selected_indices(app_context.get_check_select_pose_state())
        poselist = app_context.camera_manager.poselist
        for i in selected_indices:
            vis2.add_geometry(poselist[i])
        
        # 启用位姿索引控件
        app_context.set_pose_index_enabled(True)
        app_context.set_pose_index_maximum(len(selected_indices))
        
        QMessageBox.information(app_context.main_window, "任务完成", "位姿优化完成")