class AppContext:
    """应用上下文，提供数据和服务访问"""
    def __init__(self):
        self.data_manager = None
        self.task_manager = None
        self.camera_manager = None
        self.visualization_manager = None
        self.main_window = None
    
    def setup(self, main_window):
        """初始化上下文"""
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.task_manager = main_window.task_manager
        self.camera_manager = main_window.camera_manager
        self.visualization_manager = main_window.visualization_manager
    
    # 数据访问方法
    def get_root_path(self):
        return self.data_manager.root if self.data_manager else None
    
    def get_images(self):
        return self.data_manager.images if self.data_manager else []
    
    def get_pcd_files(self):
        return self.data_manager.pcdfiles if self.data_manager else []
    
    def get_selected_indices(self, check_state=0):
        return self.data_manager.selected[check_state] if self.data_manager else []
    
    def get_trajectory(self):
        return self.data_manager.traj if self.data_manager else None
    
    def get_trajectory_selected(self):
        return self.data_manager.traj_selected if self.data_manager else None
    
    # UI访问方法
    def get_voxel_size(self):
        return float(self.main_window.voxelsize.text()) if self.main_window else 0.01
    
    def get_trunction(self):
        return float(self.main_window.trunction.text()) if self.main_window else 0.04
    
    def get_min_weight(self):
        return float(self.main_window.minweight.text()) if self.main_window else 3.0
    
    def get_component(self):
        return int(self.main_window.component.text()) if self.main_window else 1000
    
    def get_iteration(self):
        return int(self.main_window.iteration.text()) if self.main_window else 5
    
    def get_color_iteration(self):
        return self.main_window.ColorIteration.text() if self.main_window else "5"
    
    def update_mesh_path(self, path):
        if self.main_window:
            self.main_window.MeshPath.setText(path)
    
    def update_root_label(self, path):
        if self.main_window:
            self.main_window.RootLabel.setText(f'当前目录：{path}')
    
    def get_vis1(self):
        return self.main_window.vis1 if self.main_window else None
    
    def get_vis2(self):
        return self.main_window.vis2 if self.main_window else None
    
    def get_point_pose_index(self):
        return self.main_window.PointPoseIndex.value() if self.main_window else 1
    
    def get_pose_index(self):
        return self.main_window.PoseIndex.value() if self.main_window else 1
    
    def set_point_pose_index_enabled(self, enabled):
        if self.main_window:
            self.main_window.PointPoseIndex.setEnabled(enabled)
    
    def set_point_pose_index_maximum(self, maximum):
        if self.main_window:
            self.main_window.PointPoseIndex.setMaximum(maximum)
    
    def set_pose_index_enabled(self, enabled):
        if self.main_window:
            self.main_window.PoseIndex.setEnabled(enabled)
    
    def set_pose_index_maximum(self, maximum):
        if self.main_window:
            self.main_window.PoseIndex.setMaximum(maximum)
    
    def get_check_select_pose_state(self):
        return self.main_window.CheckSelectPose.checkState() if self.main_window else 0

# 全局上下文实例
app_context = AppContext()