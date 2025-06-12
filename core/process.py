import open3d as o3d
import numpy as np
import os
from multiprocessing import Process, Queue
import vdbfusion
import utils
import copy
import subprocess
def pointfilter(data_queue, result_queue):

    data = data_queue.get()
    pcd = data['pcd']
    pointcloud = o3d.geometry.PointCloud()
    pointcloud.points = o3d.utility.Vector3dVector(pcd)
    labels = np.array(
            pointcloud.cluster_dbscan(eps=0.02, min_points=30, print_progress=True))
    result_queue.put(labels)

def get_mesh(data_queue, result_queue):
    data = data_queue.get()
    labels = data['labels']
    voxelsize = data['voxelsize']
    trunction = data['trunction']
    minweight = data['minweight']
    component = data['component']
    iteration = data['iteration']
    traj_file = data['traj_file']
    dataset_path = data['dataset_path']
    pcdfiles = data['pcdfiles']
    print("Initializing VDBVolume...")
    vdb_volume = vdbfusion.VDBVolume(voxel_size=voxelsize, sdf_trunc=trunction)
    
    trajectories = utils.traj_read(traj_file)

    # Integrate all point clouds into the VDBVolume
    print(len(labels))
    start_index = 0
    for i in range(len(pcdfiles)):
        pcd = o3d.io.read_point_cloud(dataset_path + pcdfiles[i])
        scan = np.asarray(pcd.points)
        pcd_new = []
        for j in range(len(scan)):
            if labels[start_index+j] != -1:
                pcd_new.append(scan[j])
        start_index += len(scan)    
        scan = np.asarray(pcd_new)    
        origin = trajectories[i]
        vdb_volume.integrate(scan, origin)
    # Extract triangle mesh

    vert, tri = vdb_volume.extract_triangle_mesh(min_weight=minweight)

    # Create Open3D mesh object

    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(vert),
        o3d.utility.Vector3iVector(tri),
    )

    # Cluster mesh facets for connected filtering.

    triangle_clusters, cluster_n_triangles, cluster_area = (
            mesh.cluster_connected_triangles()
    )
    triangle_clusters = np.asarray(triangle_clusters)
    cluster_n_triangles = np.asarray(cluster_n_triangles)
    cluster_area = np.asarray(cluster_area)

    # Filter floating facets in mesh

    mesh_0 = copy.deepcopy(mesh)
    triangles_to_remove = cluster_n_triangles[triangle_clusters] < component
    mesh_0.remove_triangles_by_mask(triangles_to_remove)

    # Filter with Average filter

    mesh_out = mesh_0.filter_smooth_simple(number_of_iterations=iteration)
    mesh_out.compute_vertex_normals()
    
    # Save the mesh
    print("Saving the mesh to mesh.ply...")
    # 确保顶点数据是浮点格式
    vertices = np.asarray(mesh_out.vertices, dtype=np.float32)
    
    # 创建一个新的网格对象
    new_mesh = o3d.geometry.TriangleMesh()
    new_mesh.vertices = o3d.utility.Vector3dVector(vertices)
    new_mesh.triangles = mesh_out.triangles  # 保留原始的三角形信息

    # 检查并复制法线
    if mesh_out.has_vertex_normals():
        new_mesh.vertex_normals = mesh_out.vertex_normals
    
    old_string = "double"
    new_string = "float"

    file_path = dataset_path+f"{voxelsize}_{trunction}_{minweight}_{component}_{iteration}.ply"
    o3d.io.write_triangle_mesh(file_path, new_mesh,write_ascii=True)
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 替换前13行中的指定字符串
    for i in range(min(13, len(lines))):
        lines[i] = lines[i].replace(old_string, new_string)
    # 将修改后的内容写回文件
    with open(file_path, 'w') as file:
        file.writelines(lines)
    result_queue.put(file_path)

def get_depth(data_queue, result_queue):

    data = data_queue.get()
    dataset_path = data['dataset_path']
    mesh_path = data['mesh_path']
    utils.clear_directory("/home/zzz/code/ui/test/project/work/depth")
    utils.clear_directory("/home/zzz/code/ui/test/project/work/visualdepth")
    utils.clear_directory("/home/zzz/code/ui/test/project/work/blend")
    subprocess.run(f"./ext/getdepth/MyOpenGLProject {dataset_path} {mesh_path}", shell=True)
    result_queue.put('success')

def optimize(data_queue, result_queue):

    data = data_queue.get()
    directory_depth = data['directory_depth']
    directory_color = data['directory_color']
    color_paths = data['color_paths']
    selected = data['selected']
    checkselect = data['checkselect']
    dataset_path = data['dataset_path']
    mesh_path = data['mesh_path']
    coloriteration = data['coloriteration']

    mesh = None
    rgbd_images = []
    camera_trajectory = None
    depth_paths = utils.sort_files_by_number(directory_depth,'png')

    for i in range(len(selected[checkselect])):
        depth = o3d.io.read_image(directory_depth+depth_paths[i])
        color = o3d.io.read_image(directory_color+color_paths[selected[checkselect][i]])
        print(depth_paths[i])
        print(color_paths[selected[checkselect][i]])
        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color, depth, convert_rgb_to_intensity=False)
        rgbd_images.append(rgbd_image)
    camera_trajectory = o3d.io.read_pinhole_camera_trajectory(
        dataset_path + "traj.log")
    

    camera_trajectory.parameters = [para for index,para in enumerate(camera_trajectory.parameters) if index in selected[checkselect]]

    mesh = o3d.io.read_triangle_mesh(
        mesh_path)
    mesh.compute_vertex_normals()
    intrinsic = o3d.camera.PinholeCameraIntrinsic(
        width=1280,
        height=1024,
        fx = 1302.39546,
        fy = 1301.80638,
        cx = 689.52858,
        cy = 504.24215
    )
    for param in camera_trajectory.parameters:
        param.intrinsic = intrinsic
    
    print(mesh_path)
    print(len(camera_trajectory.parameters))
    print(len(rgbd_images))
    # Before full optimization, let's visualize texture map
    # with given geometry, RGBD images, and camera poses.
    mesh, camera_trajectory = o3d.pipelines.color_map.run_rigid_optimizer(
        mesh, rgbd_images, camera_trajectory,
        o3d.pipelines.color_map.RigidOptimizerOption(maximum_iteration=(int)(coloriteration)))
    path = os.path.splitext(mesh_path)[0]  # 直接去掉扩展名
    o3d.io.write_triangle_mesh(path+f'_iter{coloriteration}.ply', mesh)
    result_queue.put(path+f'_iter{coloriteration}.ply')

def mvstexturing(data_queue, result_queue):
    # 指定你想统计的目录路径（可以是绝对路径或相对路径）
    data = data_queue.get()
    target_dir = data['target_dir']
    mesh_path = data['mesh_path']
    dataset_path = data['dataset_path']
    # 获取该目录下的所有文件和文件夹
    all_items = os.listdir(target_dir)
    # 统计文件数量（排除文件夹）
    file_count = 0
    file_count = sum(1 for item in all_items if os.path.isdir(os.path.join(target_dir, item)))
    subprocess.run(f"mkdir /home/zzz/code/ui/test/project/work/meshobj/obj_{file_count}", shell=True)
    subprocess.run(f"./ext/mvs-texturing/apps/texrecon/texrecon --outlier_removal=gauss_damping --tone_mapping=gamma --keep_unseen_faces --num_threads=8 {dataset_path} {mesh_path} /home/zzz/code/ui/test/project/work/meshobj/obj_{file_count}/result", shell=True)
    obj_file_path = f'/home/zzz/code/ui/test/project/work/meshobj/obj_{file_count}'+'/result.obj'
    result_queue.put(obj_file_path)
