from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap

class VideoWidget(QLabel):
    """
    Custom QLabel that handles video frame rendering with aspect ratio preservation,
    and supports drawing a gate line interactively.
    """
    line_drawn = Signal(tuple, tuple)  # Emits (pt1, pt2) in relative coordinates

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 360)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.drawing_mode = False
        self.is_drawing = False
        self.start_pt = QPoint()
        self.current_pt = QPoint()
        
        # Default relative line coordinates (will be drawn by worker frame overlay)
        self.rel_pt1 = (0.1, 0.5)
        self.rel_pt2 = (0.9, 0.5)
        
        self.original_pixmap = None

    def set_drawing_mode(self, enabled):
        """
        Enables or disables interactive line drawing mode.
        """
        self.drawing_mode = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_frame(self, q_img):
        """
        Sets the current video frame and updates the display.
        """
        self.original_pixmap = QPixmap.fromImage(q_img)
        self.update_display()

    def update_display(self):
        """
        Scales the original frame pixmap to fit the label while keeping the aspect ratio.
        """
        if self.original_pixmap is None:
            # Place-holder if no video is loaded yet
            self.setText("Please open a video stream to start")
            self.setStyleSheet("color: #64748B; font-size: 16px; font-weight: bold;")
            return
            
        scaled = self.original_pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def widget_to_relative(self, pos):
        """
        Maps local widget pixel coordinates to relative (0.0 to 1.0) coordinates
        with respect to the active video frame viewport.
        """
        if self.pixmap() is None:
            return (0.0, 0.0)
            
        pm = self.pixmap()
        pm_w = pm.width()
        pm_h = pm.height()
        
        lbl_w = self.width()
        lbl_h = self.height()
        
        # Calculate margins since image is centered
        offset_x = (lbl_w - pm_w) / 2.0
        offset_y = (lbl_h - pm_h) / 2.0
        
        # Clamp coordinates to the frame bounding box
        x = max(0.0, min(pos.x() - offset_x, pm_w))
        y = max(0.0, min(pos.y() - offset_y, pm_h))
        
        # Return relative coordinates
        return (x / pm_w, y / pm_h)

    def mousePressEvent(self, event):
        if self.drawing_mode and event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = True
            self.start_pt = event.position().toPoint()
            self.current_pt = event.position().toPoint()
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.current_pt = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_drawing and event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = False
            end_pt = event.position().toPoint()
            
            # Map start/end points to relative video space
            rel_p1 = self.widget_to_relative(self.start_pt)
            rel_p2 = self.widget_to_relative(end_pt)
            
            # Ensure line has a valid length (ignore micro-clicks)
            dx = rel_p1[0] - rel_p2[0]
            dy = rel_p1[1] - rel_p2[1]
            if (dx*dx + dy*dy) > 0.001:
                self.rel_pt1 = rel_p1
                self.rel_pt2 = rel_p2
                self.line_drawn.emit(rel_p1, rel_p2)
                
            self.drawing_mode = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        # Render dynamic visual feedback (dotted orange line) when user is drawing
        if self.is_drawing:
            painter = QPainter(self)
            pen = QPen(QColor(255, 165, 0), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.start_pt, self.current_pt)
            painter.end()
