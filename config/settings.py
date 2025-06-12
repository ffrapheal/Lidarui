"""应用配置文件"""

# 相机内参
CAMERA_INTRINSICS = {
    'fx': 1302.39546,
    'fy': 1301.80638,
    'cx': 689.52858,
    'cy': 504.24215,
    'width': 1280,
    'height': 1024
}

# 颜色配置
COLORS = {
    'normal_camera': [0.1, 0.5, 0.9],
    'selected_camera': [1, 0, 0],
    'background': [0.6, 0.6, 0.6],
    'pointcloud': [0.5, 0.5, 0.5]
}

# 路径配置
PATHS = {
    'work_dir': './work/',
    'data_dir': './Data/',
    'stylesheets': './stylesheets/test.qss',
    'background_image': './images/bg1.png'
}

# 默认参数
DEFAULT_PARAMS = {
    'voxel_size': 0.01,
    'trunction': 0.04,
    'min_weight': 3.0,
    'component': 1000,
    'iteration': 5,
    'color_iteration': '5',
    'sampling_ratio': 0.1,
    'point_size': 0.2,
    'camera_scale': 0.05
}

# UI配置
UI_CONFIG = {
    'window_size': (1920 * 2, 1080 * 2),
    'timer_interval': 20,
    'progress_check_interval': 1000,
    'max_point_dialogs': 2
}