from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtGui import QPainter, QCursor, QBitmap, QPen, QColor
from PySide2.QtCore import Qt, QTimer

class CursorGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_visible = False

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 增大窗口大小以容纳十字
        cross_size = 20  # 十字大小
        self.resize(
            cross_size // self.devicePixelRatio(),
            cross_size // self.devicePixelRatio()
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.setInterval(16)  # ~60Hz更新频率

        self.blank_cursor = QCursor(QBitmap(1, 1), QBitmap(1, 1))  # 1x1透明光标

        self.hide()

    def update_position(self):
        """跟随鼠标移动窗口"""
        if not self.is_visible:
            return
        global_pos = QCursor.pos()
        # 计算窗口位置（使图标中心对准鼠标位置）
        x = global_pos.x() - self.width() // 2
        y = global_pos.y() - self.height() // 2
        self.move(x, y)

    def paintEvent(self, event):
        """绘制自定义光标图标"""
        if not self.is_visible:
            return

        painter = QPainter(self)

        # 设置抗锯齿渲染
        painter.setRenderHint(QPainter.Antialiasing)

        # 将坐标系原点移动到窗口中心
        painter.translate(self.width() / 2, self.height() / 2)

        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)

        # 绘制十字
        size = 8  # 十字大小的一半
        painter.drawLine(-size, 0, size, 0)  # 水平线
        painter.drawLine(0, -size, 0, size)  # 垂直线

    def show_cursor(self, flag):
        if flag:
            self.is_visible = True
            self.show()
            self.timer.start()
            QApplication.setOverrideCursor(self.blank_cursor)
        else:
            self.is_visible = False
            self.timer.stop()
            self.hide()
            QApplication.restoreOverrideCursor()