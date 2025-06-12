import open3d as o3d
import numpy as np

class CameraManager:
    def __init__(self):
        self.poselist = []
        self.normal_color = [0.1, 0.5, 0.9]
        self.selected_color = [1, 0, 0]
    
    def setup_cameras(self, trajectory):
        """设置相机位姿"""
        self.poselist = []
        
        for i, param in enumerate(trajectory.parameters):
            camera = o3d.geometry.LineSet.create_camera_visualization(
                intrinsic=param.intrinsic, 
                extrinsic=param.extrinsic, 
                scale=0.05
            )
            camera.points = o3d.utility.Vector3dVector(np.array(camera.points)[:5])
            camera.lines = o3d.utility.Vector2iVector(np.array(camera.lines)[:8])
            camera.paint_uniform_color(self.normal_color)
            self.poselist.append(camera)
    
    def update_camera_color(self, old_index, new_index, vis):
        """更新相机颜色"""
        if old_index < len(self.poselist):
            self.poselist[old_index].paint_uniform_color(self.normal_color)
            vis.update_geometry(self.poselist[old_index])
        
        if new_index < len(self.poselist):
            self.poselist[new_index].paint_uniform_color(self.selected_color)
            vis.update_geometry(self.poselist[new_index])