from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter, QColor, QPen

class IndicatorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 初始化轴量值（范围0-1）
        self.throttle_value = 0  # 油门轴值
        self.rudder_value = 0.5    # 方向舵轴值

        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

    def set_throttle_value(self, value):
        """设置油门轴量值（0到1之间）"""
        self.throttle_value = max(0, min(1, value))
        self.update()

    def set_rudder_value(self, value):
        """设置方向舵轴量值（0到1之间）"""
        self.rudder_value = max(0, min(1, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制油门轴（垂直）
        self.draw_throttle_axis(painter)

        # 绘制方向舵轴（水平）
        self.draw_rudder_axis(painter)

    def draw_throttle_axis(self, painter):
        """绘制垂直的油门轴"""
        # 计算位置和尺寸
        screen_rect = self.geometry()
        base_x = 50  # 距离屏幕左侧50像素
        base_y = screen_rect.height() - 50  # 距离屏幕底部50像素
        line_height = 150  # 竖线高度

        # 绘制主竖线
        pen = QPen(QColor(255, 0, 0), 2)  # 红色，2像素宽
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x, base_y - line_height)

        # 绘制底部横线（半透明）
        pen.setColor(QColor(255, 0, 0, 128))  # 半透明红色
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(base_x - 7.5, base_y, base_x + 7.5, base_y)

        # 绘制顶部横线（半透明）
        painter.drawLine(base_x - 7.5, base_y - line_height * .75, base_x + 7.5, base_y - line_height * .75)

        # 绘制表示油门轴量的横线（深红色）
        indicator_y = base_y - int(self.throttle_value * line_height)
        pen.setColor(QColor(200, 0, 0))  # 深红色
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(base_x - 10, indicator_y, base_x + 10, indicator_y)

    def draw_rudder_axis(self, painter):
        """绘制水平的方向舵轴"""
        # 计算位置和尺寸
        screen_rect = self.geometry()
        base_x = 75  # 距离屏幕左侧50像素（与油门轴对齐）
        base_y = screen_rect.height() - 50  # 距离屏幕底部50像素（与油门轴对齐）
        line_length = 100  # 横线长度

        # 绘制主横线
        pen = QPen(QColor(255, 0, 0), 2)  # 蓝色，2像素宽
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x + line_length, base_y)

        pen.setColor(QColor(255, 0, 0, 128))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(base_x + line_length / 2, base_y - 5, base_x + line_length / 2, base_y + 5)

        # 绘制表示方向舵轴量的竖线（深蓝色）
        indicator_x = base_x + int(self.rudder_value * line_length)
        pen.setColor(QColor(200, 0, 0))  # 深蓝色
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(indicator_x, base_y - 10, indicator_x, base_y + 10)

    def show_overlay(self, show: bool):
        """控制overlay窗口的显示与隐藏"""
        self.is_visible = show
        if show:
            self.show()
        else:
            self.hide()
