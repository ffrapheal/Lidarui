"""文件操作工具函数"""
import os
import shutil
import numpy as np
import os
import shutil
import re
from scipy.linalg import norm


def clear_directory(directory_path):
    """清空目录"""
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'删除 {file_path} 失败. 原因: {e}')

def ensure_directory_exists(directory_path):
    """确保目录存在"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_file_extension(file_path):
    """获取文件扩展名"""
    return os.path.splitext(file_path)[1].lower()

def is_image_file(file_path):
    """检查是否为图像文件"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    return get_file_extension(file_path) in image_extensions

def is_point_cloud_file(file_path):
    """检查是否为点云文件"""
    pc_extensions = ['.pcd', '.ply', '.xyz', '.pts']
    return get_file_extension(file_path) in pc_extensions

def ray_triangle_intersect(ray_origin, ray_direction, v0, v1, v2):
    """射线与三角形相交检测"""
    epsilon = 1e-8
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = np.cross(ray_direction, edge2)
    a = np.dot(edge1, h)
    if -epsilon < a < epsilon:
        return False, None  # This ray is parallel to this triangle.
    f = 1.0 / a
    s = ray_origin - v0
    u = f * np.dot(s, h)
    if not (0.0 <= u <= 1.0):
        return False, None
    q = np.cross(s, edge1)
    v = f * np.dot(ray_direction, q)
    if not (0.0 <= v <= 1.0):
        return False, None
    if u + v > 1.0:
        return False, None
    t = f * np.dot(edge2, q)
    if t > epsilon:
        intersect_point = ray_origin + ray_direction * t
        return True, intersect_point
    else:
        return (
            False,
            None,
        )  # This means that there is a line intersection but not a ray intersection.

def extract_number(filename):
    """提取文件名中的数字部分"""
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0

def sort_files_by_number(directory, suffix):
    """按数字顺序排序文件名"""
    files = os.listdir(directory)
    
    files = [f for f in files if f.endswith(suffix)]

    # 按数字顺序排序文件名
    sorted_files = sorted(files, key=extract_number)

    return sorted_files

def write_to_file(list,path):
    """写入文件"""
    with open(path,'w')as file:
        for index in list:
            file.write(str(index)+'\n')

def read_from_file(path):
    """读取文件"""
    list = []
    with open(path,'r')as file:
        for line in file:
            list.append(int(line))
    return list

def se3_log_norm(T):
    """计算SE(3)矩阵的李代数(se(3))表示的范数"""
    R = T[:3, :3]
    t = T[:3, 3]
    
    # 计算旋转部分的对数(so(3))
    theta = np.arccos(np.clip((np.trace(R) - 1) / 2, -1.0, 1.0))
    
    if theta < 1e-6:
        # 当旋转很小时，使用近似
        w_hat = (R - R.T) / 2
    else:
        w_hat = (R - R.T) * theta / (2 * np.sin(theta))
    
    # 提取旋转向量
    w = np.array([w_hat[2, 1], w_hat[0, 2], w_hat[1, 0]])
    
    # 计算平移部分
    if theta < 1e-6:
        rho = t
    else:
        A = np.sin(theta)/theta
        B = (1 - np.cos(theta))/(theta**2)
        V_inv = np.eye(3) - 0.5 * w_hat + (1/theta**2) * (1 - A/(2*B)) * np.dot(w_hat, w_hat)
        rho = np.dot(V_inv, t)
    
    # 直接返回李代数向量的范数
    return norm(np.concatenate([rho, w]))

def quaternion_to_rotation_matrix(q):
    """将四元数转换为旋转矩阵"""
    w, x, y, z = q
    R = np.array([
        [1 - 2*y**2 - 2*z**2, 2*x*y - 2*w*z, 2*x*z + 2*w*y],
        [2*x*y + 2*w*z, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*w*x],
        [2*x*z - 2*w*y, 2*y*z + 2*w*x, 1 - 2*x**2 - 2*y**2]
    ])
    return R

def select_keyframes_by_norm(poses, index_notblur, norm_thresh=0.3):
    """
    使用李代数范数直接筛选位姿变化大的关键帧
    
    参数:
        poses: 位姿列表, 每个位姿是4x4的SE(3)矩阵
        norm_thresh: 李代数范数阈值
        
    返回:
        关键帧索引列表
    """
    if len(poses) == 0:
        return []
    
    keyframes = [index_notblur[0]]  # 总是选择第一帧
    last_pose = poses[index_notblur[0]]
    
    for i in range(1, len(index_notblur)):
        # 计算相对位姿
        T_rel = np.dot(np.linalg.inv(last_pose), poses[index_notblur[i]])
        
        # 计算李代数范数
        current_norm = se3_log_norm(T_rel)
        
        if current_norm > norm_thresh:
            keyframes.append(index_notblur[i])
            last_pose = poses[index_notblur[i]]
    
    return keyframes

def get_poses(path):
    """获取位姿列表"""
    poses=[]
    files = sort_files_by_number(path,'txt')
    for filename in files:
        file_path = os.path.join(path, filename)
        # 读取 .txt 文件的内容
        with open(file_path, 'r') as infile:
            data = np.loadtxt(file_path, dtype=float)
            q = data[4:]
            R = quaternion_to_rotation_matrix(q)
            t = data[1:4]
            T = np.eye(4)
            T[:3, :3] = R
            T[:3, 3] = t
            poses.append(T)
    return poses

def generate_trajectory_file(input_directory, output_file):
    """生成open3d中colormap需要的轨迹文件"""
    with open(output_file, 'w') as outfile:
        index = 0
        for filename in sort_files_by_number(input_directory,'txt'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r') as infile:
                data = np.loadtxt(file_path, dtype=float)
                outfile.write(f"{index} {index} {index + 1}\n")
                q = data[4:]
                R = quaternion_to_rotation_matrix(q)
                t = data[1:4]
                T = np.eye(4)
                T[:3, :3] = R
                T[:3, 3] = t
                outfile.write(f"{T[0,0]:.10f} {T[0,1]:.10f} {T[0,2]:.10f} {T[0,3]:.10f}\n")
                outfile.write(f"{T[1,0]:.10f} {T[1,1]:.10f} {T[1,2]:.10f} {T[1,3]:.10f}\n")
                outfile.write(f"{T[2,0]:.10f} {T[2,1]:.10f} {T[2,2]:.10f} {T[2,3]:.10f}\n")
                outfile.write(f"{T[3,0]:.10f} {T[3,1]:.10f} {T[3,2]:.10f} {T[3,3]:.10f}\n")
                index += 1
def traj_read(traj_file):
    """读取轨迹文件"""
    trajectories = []
    cur_traj = []
    with open(traj_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                if len(cur_traj) != 0:
                    trajectories.append(np.array(cur_traj, dtype=np.float64))
                    cur_traj = []
            else:
                cur_traj.append(np.array(parts, dtype=np.float64))
    trajectories.append(np.array(cur_traj, dtype=np.float64))
    trajectories.append(trajectories[len(trajectories) - 1])
    return trajectories