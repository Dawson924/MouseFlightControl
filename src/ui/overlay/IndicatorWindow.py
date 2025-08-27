from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import Qt, QPointF
from PySide2.QtGui import QPainter, QColor, QPen, QPolygonF, QBrush

class IndicatorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 初始化轴量值（范围0-1）
        self.throttle_value = 0  # 油门轴值
        self.rudder_value = 0.5    # 方向舵轴值
        self.x_axis_value = 0.5    # X轴值
        self.y_axis_value = 0.5    # Y轴值

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

    def set_xy_values(self, x_value, y_value):
        """设置XY轴量值（0到1之间）"""
        self.x_axis_value = max(0, min(1, x_value))
        self.y_axis_value = max(0, min(1, y_value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 首先绘制透明背景正方形
        self.draw_transparent_background(painter)

        # 然后绘制三个指示器
        self.draw_throttle_axis(painter)
        self.draw_rudder_axis(painter)
        self.draw_quadrant_cross(painter)

    def draw_transparent_background(self, painter):
        """绘制透明背景正方形"""
        screen_rect = self.geometry()

        # 计算正方形的位置和大小
        square_size = 180  # 正方形边长
        square_x = 30  # 距离屏幕左侧30像素
        square_y = screen_rect.height() - square_size - 30  # 距离屏幕底部30像素

        # 绘制半透明红色背景
        painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
        painter.setPen(Qt.NoPen)  # 无边框
        painter.drawRect(square_x, square_y, square_size, square_size)

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
        pen = QPen(QColor(255, 0, 0), 2)  # 红色，2像素宽
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x + line_length, base_y)

        pen.setColor(QColor(255, 0, 0, 128))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(base_x + line_length / 2, base_y - 5, base_x + line_length / 2, base_y + 5)

        # 绘制表示方向舵轴量的竖线（深红色）
        indicator_x = base_x + int(self.rudder_value * line_length)
        pen.setColor(QColor(200, 0, 0))  # 深红色
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(indicator_x, base_y - 10, indicator_x, base_y + 10)

    def draw_quadrant_cross(self, painter):
        """绘制象限十字和位置小球"""
        # 计算位置和尺寸
        screen_rect = self.geometry()
        center_x = 125
        center_y = screen_rect.height() - 125
        cross_size = 60

        # 绘制十字线
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)

        # 水平线
        painter.drawLine(center_x - cross_size, center_y, center_x + cross_size, center_y)
        # 垂直线
        painter.drawLine(center_x, center_y - cross_size, center_x, center_y + cross_size)

        # 计算小球位置
        # X轴：0=最左，1=最右；Y轴：0=最上，1=最下
        ball_x = center_x + int((self.x_axis_value - 0.5) * 2 * cross_size)
        ball_y = center_y + int((self.y_axis_value - 0.5) * 2 * cross_size)

        # 绘制空心菱形
        pen = QPen(QColor(200, 0, 0))  # 设置边框颜色
        pen.setWidth(2)  # 设置边框宽度
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  # 不使用填充（空心）

        # 定义菱形的四个顶点（以ball_x, ball_y为中心）
        diamond_points = [
            QPointF(ball_x, ball_y - 7),   # 上顶点
            QPointF(ball_x + 5, ball_y),   # 右顶点
            QPointF(ball_x, ball_y + 7),   # 下顶点
            QPointF(ball_x - 5, ball_y)    # 左顶点
        ]

        # 创建多边形并绘制
        polygon = QPolygonF(diamond_points)
        painter.drawPolygon(polygon)

    def show_overlay(self, show: bool):
        """控制overlay窗口的显示与隐藏"""
        self.is_visible = show
        if show:
            self.show()
        else:
            self.hide()