from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MeshImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("网格位姿图像")
        self.setModal(True)
        self.resize(800, 600)
        
        # 设置布局
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
    
    def display_image(self, image_path):
        """显示图像"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 缩放图像以适应窗口
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.setWindowTitle(f"网格位姿图像 - {image_path.split('/')[-1]}")
            else:
                self.image_label.setText("无法加载图像")
        except Exception as e:
            self.image_label.setText(f"加载图像失败: {str(e)}")