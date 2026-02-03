"""
图片查看器对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QFont, QWheelEvent, QMouseEvent
import io


class DraggableLabel(QLabel):
    """可拖动的图片标签"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.drag_start_position = QPoint()
        self.scroll_area = None
        
    def set_scroll_area(self, scroll_area):
        """设置关联的滚动区域"""
        self.scroll_area = scroll_area
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_position = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.dragging and self.scroll_area:
            # 计算移动距离
            delta = event.position().toPoint() - self.drag_start_position
            
            # 获取滚动条
            h_scrollbar = self.scroll_area.horizontalScrollBar()
            v_scrollbar = self.scroll_area.verticalScrollBar()
            
            # 反向移动滚动条（拖动图片向右，滚动条向左）
            h_scrollbar.setValue(h_scrollbar.value() - delta.x())
            v_scrollbar.setValue(v_scrollbar.value() - delta.y())
            
            # 更新拖动起始位置
            self.drag_start_position = event.position().toPoint()
            
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
        
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        if not self.dragging:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)


class ImageViewerDialog(QDialog):
    def __init__(self, image_data, title="查看图片", parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.original_pixmap = None
        self.current_scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.scale_step = 0.1
        self.image_label = None
        self.scroll_area = None
        self.init_ui(title)
    
    def init_ui(self, title):
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 1200, 900)  # 增大默认窗口大小
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("放大 (+)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setShortcut("Ctrl++")
        control_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("缩小 (-)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setShortcut("Ctrl+-")
        control_layout.addWidget(zoom_out_btn)
        
        reset_btn = QPushButton("重置 (1:1)")
        reset_btn.clicked.connect(self.reset_zoom)
        reset_btn.setShortcut("Ctrl+0")
        control_layout.addWidget(reset_btn)
        
        fit_btn = QPushButton("适应窗口")
        fit_btn.clicked.connect(self.fit_to_window)
        control_layout.addWidget(fit_btn)
        
        self.scale_label = QLabel("100%")
        self.scale_label.setAlignment(Qt.AlignCenter)
        self.scale_label.setMinimumWidth(60)
        control_layout.addWidget(self.scale_label)
        
        # 添加拖动提示
        drag_hint = QLabel("提示: 放大后可拖动图片")
        drag_hint.setStyleSheet("color: #666; font-size: 11px;")
        drag_hint.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(drag_hint)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 图片显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # 重要：设置为False以支持缩放
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        try:
            # 将二进制数据转换为QPixmap
            self.original_pixmap = QPixmap()
            self.original_pixmap.loadFromData(self.image_data)
            
            if self.original_pixmap.isNull():
                raise Exception("无法加载图片数据")
            
            # 创建可拖动的标签显示图片
            self.image_label = DraggableLabel()
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("border: 1px solid #ccc;")
            self.image_label.set_scroll_area(self.scroll_area)
            
            # 初始显示图片
            self.update_image()
            
            self.scroll_area.setWidget(self.image_label)
            
            # 启用鼠标滚轮缩放
            self.scroll_area.wheelEvent = self.wheel_event
            
        except Exception as e:
            error_label = QLabel(f"无法显示图片: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px;")
            self.scroll_area.setWidget(error_label)
        
        layout.addWidget(self.scroll_area)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 初始适应窗口
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.fit_to_window()
    
    def update_image(self):
        """更新图片显示"""
        if not self.original_pixmap or self.original_pixmap.isNull() or not self.image_label:
            return
        
        # 计算缩放后的尺寸
        scaled_width = int(self.original_pixmap.width() * self.current_scale)
        scaled_height = int(self.original_pixmap.height() * self.current_scale)
        
        # 缩放图片
        scaled_pixmap = self.original_pixmap.scaled(
            scaled_width, scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 更新显示
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
        
        # 更新缩放比例显示
        self.scale_label.setText(f"{int(self.current_scale * 100)}%")
    
    def zoom_in(self):
        """放大"""
        if self.current_scale < self.max_scale:
            self.current_scale = min(self.current_scale + self.scale_step, self.max_scale)
            self.update_image()
    
    def zoom_out(self):
        """缩小"""
        if self.current_scale > self.min_scale:
            self.current_scale = max(self.current_scale - self.scale_step, self.min_scale)
            self.update_image()
    
    def reset_zoom(self):
        """重置为原始大小"""
        self.current_scale = 1.0
        self.update_image()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return
        
        # 获取可用空间（减去控件占用的空间）
        available_width = self.scroll_area.width() - 20  # 留一些边距
        available_height = self.scroll_area.height() - 20
        
        # 计算适应窗口的缩放比例
        width_scale = available_width / self.original_pixmap.width()
        height_scale = available_height / self.original_pixmap.height()
        
        # 选择较小的缩放比例以确保图片完全显示
        fit_scale = min(width_scale, height_scale)
        fit_scale = max(self.min_scale, min(fit_scale, self.max_scale))
        
        self.current_scale = fit_scale
        self.update_image()
    
    def wheel_event(self, event: QWheelEvent):
        """鼠标滚轮事件处理"""
        # 检查是否按下Ctrl键（不需要Ctrl也可以缩放）
        modifiers = event.modifiers()
        
        if event.angleDelta().y() > 0:
            # 向上滚动，放大
            self.zoom_in()
        else:
            # 向下滚动，缩小
            self.zoom_out()
        
        event.accept()
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.zoom_out()
        elif event.key() == Qt.Key.Key_0:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.reset_zoom()
        else:
            super().keyPressEvent(event)