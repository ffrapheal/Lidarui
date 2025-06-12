import sys
from contextlib import contextmanager
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import QPixmap, QPoint, Qt, QPainter, QIcon
import numpy as np
import time
from glumpy import app as glumpy_app, gl, gloo
from glumpy.app.window import key as Key
import torch
CUDA_ENABLE_GL = True
from pycuda.gl import graphics_map_flags
import pycuda.driver
sys.path.append('/home/xjc/code/LargePGSR/PGSR')
from gaussian_renderer import render
from utils.general_utils import safe_state
from utils.graphics_utils import getProjectionMatrix, focal2fov, fov2focal
from argparse import ArgumentParser
from torchvision.utils import save_image
from arguments import ModelParams, PipelineParams, get_combined_args
from scene.gaussian_model import GaussianModel
from torchvision.io import read_image
import random
import copy
import os
import json
from core import *

class GSTabHandler:
    def __init__(self):
        self.setup_events()
        self.model_path = ""

    
    def setup_events(self):
        """绑定3DGS Tab相关事件"""
        main_window = app_context.main_window
        main_window.TrainButton.clicked.connect(self.on_train_button_clicked)



    def on_train_button_clicked(self):
        main_window = app_context.main_window
        modeltype = main_window.GSModel.currentText()
        datatype = main_window.DataType.currentText()

        model = train()



def train(modeltype, datatype):
    pass


@torch.no_grad()
class RenderCam():
    def __init__(self, image_width=1600, image_height=1200, FoVx = 1, FoVy=0.75):
        self.image_width = image_width
        self.image_height = image_height
        self.FoVx = FoVx
        self.FoVy = FoVy


        self.R = -torch.eye(3).cuda()
        self.T = torch.zeros(3).cuda()

        self.world_view_transform = torch.eye(4).cuda()
        self.world_view_transform[:3, :3] = self.R
        self.world_view_transform[:3, 3] = self.T

        self.zfar = 100.0
        self.znear = 0.01

        self.projection_matrix = getProjectionMatrix(self.znear, self.zfar, self.FoVx, self.FoVy).transpose(0, 1).cuda()
        # self.camera_center = self.world_view_transform.inverse()[:3, 3]
        # self.full_proj_transform = (self.world_view_transform.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0))).squeeze(0)

    @property
    def camera_center(self):
        return self.world_view_transform.inverse()[:3, 3]
    
    @property
    def full_proj_transform(self):
        return (self.world_view_transform.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0))).squeeze(0)


    @property
    def Fx(self):
        return fov2focal(self.FoVx, self.image_width)
    
    @property
    def Fy(self):
        return fov2focal(self.FoVy, self.image_height)
    
    @property
    def Cx(self):
        return 0.5 * self.image_width
    
    @property
    def Cy(self):
        return 0.5 * self.image_height
    

    def get_calib_matrix_nerf(self, scale=1.0):
        intrinsic_matrix = torch.tensor([[self.Fx/scale, 0, self.Cx/scale], [0, self.Fy/scale, self.Cy/scale], [0, 0, 1]]).float()
        extrinsic_matrix = self.world_view_transform.transpose(0,1).contiguous() # cam2world
        return intrinsic_matrix, extrinsic_matrix

    def to_c2w(self):
        return self.world_view_transform.inverse().transpose(0, 1)
    
    def from_c2w(self, c2w: torch.Tensor):
        self.world_view_transform = c2w.inverse().transpose(0, 1)
        

        # print(self.world_view_transform)

    def resize(self, width, height):
        if width>height:
            self.FoVy = self.FoVx * height / width
        else:
            self.FoVx = self.FoVy * width / height

        self.projection_matrix = getProjectionMatrix(self.znear, self.zfar, self.FoVx, self.FoVy).transpose(0, 1).cuda()
        self.image_width = width
        self.image_height = height

    def update_pos(self, move_forward, move_right, move_up, rotate_up, rotate_right, rotate_clockwise):
        
        #这里面的逻辑是先移动，后旋转
        c2w = self.world_view_transform.inverse()
        R = c2w[:3, :3]

        # 3dgs里面z轴朝前，y轴朝下，x轴朝右
        forward_dir = R@torch.Tensor([0, 0, 1])
        right_dir = R@torch.Tensor([1, 0, 0])
        up_dir = R@torch.Tensor([0, -1, 0])

        c2w[:3, 3]+=move_forward*forward_dir+move_right*right_dir+move_up*up_dir

        #先绕x轴旋转再绕y轴旋转再绕z轴旋转


class GaussianRenderer:
    '''
    用来管理一个场景的点云和一个场景的相机，并且能够输出渲染
    '''
    def __init__(self, render_width, render_height, sh = 3, model_path=None):

        # 只是用于后面的render函数，并没有什么特殊意义
        parser = ArgumentParser(description="Testing script parameters")
        self.pipeline = PipelineParams(parser)

        # 加载点云
        with torch.no_grad():
            self.gaussians = GaussianModel(sh)
            self.gaussians.load_ply(model_path)
            self.background = torch.tensor([1, 1, 1], dtype=torch.float32, device="cuda")


        self.move_speed = 0.1
        self.rotate_speed = 0.02
        self.camera_movement = torch.Tensor([0, 0, 0, 0, 0, 0]).cuda()


        self.scaling_modifier = 1000


        self.render_cam = RenderCam(FoVx=1, FoVy=render_height/render_width,
                             image_width = render_width, image_height = render_height)

    @property
    def render_width(self):
        return self.render_cam.image_width
    
    @property
    def render_height(self):
        return self.render_cam.image_height

    def get_resolution(self):
        return [self.render_width, self.render_height]
    
    def render(self):
        with torch.no_grad():
            rendering = render(self.render_cam, self.gaussians, self.pipeline, self.background, 
                               1, override_color=None, app_model=None, 
                               return_plane=True, return_depth_normal=True)
            self.render_rgb, self.render_depth, self.render_normal = rendering['render'], rendering["plane_depth"], rendering["rendered_normal"]
            self.render_normal = (self.render_normal+1)/2
        return self.render_rgb, self.render_depth, self.render_normal
    
    
    def update_camera(self):
        trans = self.camera_movement[:3]
        rot = self.camera_movement[3:]
        c2w = self.render_cam.to_c2w()
        R = c2w[:3, :3]
        C = c2w[:3, 3] +torch.Tensor(trans).cuda() @ R.T * self.move_speed
        c2w[:3, 3] = C

        rot = rot * self.rotate_speed
        Rz = torch.Tensor([
            [torch.cos(rot[2]), -torch.sin(rot[2]), 0],
            [torch.sin(rot[2]),  torch.cos(rot[2]), 0],
            [0, 0, 1]
        ]).cuda()
        Ry = torch.Tensor([
            [torch.cos(rot[1]), 0, -torch.sin(rot[1])],
            [0, 1, 0],
            [torch.sin(rot[1]), 0,  torch.cos(rot[1])]
        ]).cuda()
        Rx = torch.Tensor([
            [1, 0, 0],
            [0, torch.cos(rot[0]), -torch.sin(rot[0])],
            [0, torch.sin(rot[0]),  torch.cos(rot[0])]
        ]).cuda()
        R = R @ Rz @ Ry @ Rx
        c2w[:3, :3] = R
        self.render_cam.from_c2w(c2w)
    



class RenderView():
    def __init__(self, model_path, render_width, render_height):
        glumpy_app.use("qt5")
        self.view = glumpy_app.Window(color=(1, 1, 1, 1))
        self.screen = None
        import pycuda.gl.autoinit
        self.view._native_window
        self.view.set_handler("on_init", self.on_init)
        self.view.set_handler("on_draw", self.on_draw)
        self.view.set_handler("on_resize", self.on_resize)

        if model_path == "":
            model_path="/home/xjc/code/PGSR/output/rubble_block1/point_cloud/iteration_30000/point_cloud.ply"

        self.gaussian = GaussianRenderer(render_width, render_height, sh = 3, model_path=model_path)
        self.gaussian_list = [self.gaussian]
        self.gaussian_idx = 0
        
        self.w, self.h = render_width,render_height
        self.view._native_window.setMinimumSize(self.w, self.h)
        # self.state = torch.zeros([1, 3, self.h, self.w], dtype=torch.float32, device='cuda')
        self.create_shared_texture(self.w,self.h,4)

        vertex_ = """
        uniform float scale;
        attribute vec2 position;
        attribute vec2 texcoord;
        varying vec2 v_texcoord;
        void main()
        {
            v_texcoord = texcoord;
            gl_Position = vec4(scale*position, 0.0, 1.0);
        } """
        fragment_ = """
        uniform sampler2D tex;
        varying vec2 v_texcoord;
        void main()
        {
            gl_FragColor = texture2D(tex, v_texcoord);
        } """
        # Build the program and corresponding buffers (with 4 vertices)
        self.screen = gloo.Program(vertex_, fragment_, count=4)
        # Upload data into GPU
        self.screen['position'] = [(-1,-1), (-1,+1), (+1,-1), (+1,+1)]
        self.screen['texcoord'] = [(0,0), (0,1), (1,0), (1,1)]
        self.screen['scale'] = 1.0
        self.screen['tex'] = self.tex

        
        @self.view.event
        def on_key_press(k, mod):
            # print(Key.A, 0x061, k) # weird bugs in keymap, letters should subtract 0x20
            camera_movement = self.gaussian.camera_movement
            if k == Key.D - 0x20:
                camera_movement[0] = 1
            if k == Key.A - 0x20:
                camera_movement[0] = -1
            if k == Key.Q - 0x20:
                camera_movement[1] = 1
            if k == Key.E - 0x20:
                camera_movement[1] = -1
            if k == Key.W - 0x20:
                camera_movement[2] = 1
            if k == Key.S - 0x20:
                camera_movement[2] = -1        
            if k == Key.I - 0x20:
                camera_movement[3] = 1
            if k == Key.K - 0x20:
                camera_movement[3] = -1
            if k == Key.J - 0x20:
                camera_movement[4] = 1
            if k == Key.L - 0x20:
                camera_movement[4] = -1
            if k == Key.O - 0x20:
                camera_movement[5] = 1
            if k == Key.U - 0x20:
                camera_movement[5] = -1
                

        @self.view.event
        def on_key_release(k, mod):
            camera_movement = self.gaussian.camera_movement
            if k == Key.D - 0x20:
                camera_movement[0] = 0
            if k == Key.A - 0x20:
                camera_movement[0] = 0
            if k == Key.Q - 0x20:
                camera_movement[1] = 0
            if k == Key.E - 0x20:
                camera_movement[1] = 0
            if k == Key.W - 0x20:
                camera_movement[2] = 0
            if k == Key.S - 0x20:
                camera_movement[2] = 0        
            if k == Key.I - 0x20:
                camera_movement[3] = 0
            if k == Key.K - 0x20:
                camera_movement[3] = 0
            if k == Key.J - 0x20:
                camera_movement[4] = 0
            if k == Key.L - 0x20:
                camera_movement[4] = 0
            if k == Key.O - 0x20:
                camera_movement[5] = 0
            if k == Key.U - 0x20:
                camera_movement[5] = 0


    @contextmanager
    def cuda_activate(self, img):
        """Context manager simplifying use of pycuda.gl.RegisteredImage"""
        mapping = img.map()
        yield mapping.array(0,0)
        mapping.unmap()

    def create_shared_texture(self, w, h, c=4,
            map_flags=graphics_map_flags.WRITE_DISCARD,
            dtype=np.uint8):
        """Create and return a Texture2D with gloo and pycuda views."""
        self.tex = np.zeros((h,w,c), dtype).view(gloo.Texture2D)
        self.tex.activate() # force gloo to create on GPU
        self.tex.deactivate()
        self.cuda_buffer = pycuda.gl.RegisteredImage(
            int(self.tex.handle), self.tex.target, map_flags)
        
        if self.screen!=None:
            self.screen['tex'] = self.tex

    def on_init(self):
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glPolygonOffset(1, 1)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(2.5)

    def on_draw(self, dt):

        self.gaussian.update_camera()

        h,w = self.tex.shape[:2]
        self.rgb, self.depth, self.normal = self.gaussian.render()
        
        img = torch.clamp(self.rgb, 0, 1)
        tensor = img.squeeze().permute([1, 2, 0]).flip(0).data # put in texture order
        tensor = torch.cat((tensor, tensor[:,:,:1]),2) # add the alpha channel
        tensor[:,:,3] = 1 # set alpha
        tensor = (255*tensor).byte().contiguous() # convert to ByteTensor
        assert self.tex.nbytes == tensor.numel()*tensor.element_size()
        with self.cuda_activate(self.cuda_buffer) as ary:
            cpy = pycuda.driver.Memcpy2D()
            cpy.set_src_device(tensor.data_ptr())
            cpy.set_dst_array(ary)
            cpy.width_in_bytes = cpy.src_pitch = cpy.dst_pitch = self.tex.nbytes//h
            cpy.height = h
            cpy(aligned=False)
            torch.cuda.synchronize()
        # window.clear()
        self.screen.draw(gl.GL_TRIANGLE_STRIP)
       

    def on_resize(self, width, height):
        show_w, show_h = self.view._native_window.size().width(), self.view._native_window.size().height()
        self.gaussian.render_cam.resize(show_w, show_h)
        self.create_shared_texture(show_w, show_h)
        
        

    def on_sclaing_slider(self, value):
        self.gaussian.scaling_modifier = value
    def on_use_free_mode(self, is_checked):
        if is_checked:
            self.gaussian.render_cam = copy.copy(self.gaussian.play_cam)
            self.gaussian.play_mode = False
    def on_use_play_mode(self, is_checked):
        if is_checked:
            self.gaussian.play_mode = True
            self.gaussian.play_pause = False
            self.gaussian.select_mode = False

    def on_move_speed(self, value):
        self.gaussian.move_speed = value * 0.1
        self.view._native_window.setFocus()

    def on_rotate_speed(self, value):
        self.gaussian.rotate_speed = value * 0.02
        self.view._native_window.setFocus()

    def addGaussian(self, model_path, render_width, render_height):
        self.gaussian_list.append(GaussianRenderer(render_width, render_height, model_path))
        # if self.gaussian_idx == -1:
        #     self.gaussian_idx = 0
        #     self.gaussian = self.gaussian_list[self.gaussian_idx]
        return len(self.gaussian_list) - 1

    def deleteGaussian(self, idx):
        # print(f'Delete: {idx}/{len(self.gaussian_list)}', end=' ')
        del self.gaussian_list[idx]
        torch.cuda.empty_cache()
        self.gaussian_idx = min(1, len(self.gaussian_list) - 1)
        self.view._native_window.setFocus()

        # print(f'-> {self.gaussian_idx}/{len(self.gaussian_list)}')

    def changeGaussianIdx(self, idx, scaling_modifier, play_mode, move_speed, rotate_speed, label_key_count):
        # print(f'Change: {self.gaussian_idx}/{len(self.gaussian_list)} -> {idx}/{len(self.gaussian_list)}')
        self.gaussian_idx = idx
        # print(len(self.gaussian_list), self.gaussian_idx)
        self.gaussian = self.gaussian_list[self.gaussian_idx]
        self.gaussian.scaling_modifier = scaling_modifier
        self.gaussian.play_mode = play_mode
        self.gaussian.move_speed = move_speed * 0.1
        self.gaussian.rotate_speed = rotate_speed * 0.02

        label_key_count.setText(f'关键帧数量：{len(self.gaussian.key_views)}')
        self.view._native_window.setFocus()