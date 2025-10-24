from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import Qt, QPointF, QTimer
from PySide2.QtGui import QPainter, QColor, QPen, QPolygonF, QBrush

class IndicatorWindow(QWidget):
    def __init__(self, parent=None, x=30, y=-30):
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

        # 目标值：接收外部传入值
        self.target_throttle = 0.0
        self.target_rudder = 0.5
        self.target_x = 0.5
        self.target_y = 0.5
        # 当前值：用于绘图的平滑值
        self.current_throttle = self.target_throttle
        self.current_rudder = self.target_rudder
        self.current_x = self.target_x
        self.current_y = self.target_y

        # 固定刷新定时器
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(4)
        self.refresh_timer.timeout.connect(self._smooth_update_and_paint)
        self.refresh_timer.start()

        # 屏幕与窗口参数
        self.screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(self.screen_rect)

        # 使用传入的x、y坐标
        self.bg_square_size = 180
        if x < 0:
            self.bg_square_x = self.screen_rect.width() - self.bg_square_size - abs(x)
        else:
            self.bg_square_x = x
        if y < 0:
            self.bg_square_y = self.screen_rect.height() - self.bg_square_size - abs(y)
        else:
            self.bg_square_y = y

    def set_throttle_value(self, value):
        self.target_throttle = max(0.0, min(1.0, value))

    def set_rudder_value(self, value):
        self.target_rudder = max(0.0, min(1.0, value))

    def set_xy_values(self, x_value, y_value):
        self.target_x = max(0.0, min(1.0, x_value))
        self.target_y = max(0.0, min(1.0, y_value))

    # 动态修改窗口位置
    def set_position(self, x, y):
        self.bg_square_x = x
        self.bg_square_y = y
        self.update()

    def _smooth_update_and_paint(self):
        smooth_factor = 0.15  # 平滑系数（0.05-0.2）

        # 油门轴平滑
        if abs(self.current_throttle - self.target_throttle) > 0.001:
            self.current_throttle += (self.target_throttle - self.current_throttle) * smooth_factor
        else:
            self.current_throttle = self.target_throttle

        # 方向舵轴平滑
        if abs(self.current_rudder - self.target_rudder) > 0.001:
            self.current_rudder += (self.target_rudder - self.current_rudder) * smooth_factor
        else:
            self.current_rudder = self.target_rudder

        # XY轴平滑
        if abs(self.current_x - self.target_x) > 0.001:
            self.current_x += (self.target_x - self.current_x) * smooth_factor
        else:
            self.current_x = self.target_x

        if abs(self.current_y - self.target_y) > 0.001:
            self.current_y += (self.target_y - self.current_y) * smooth_factor
        else:
            self.current_y = self.target_y

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.draw_transparent_background(painter)
        # 传入平滑后的当前值绘图
        self.draw_throttle_axis(painter, self.current_throttle)
        self.draw_rudder_axis(painter, self.current_rudder)
        self.draw_quadrant_cross(painter, self.current_x, self.current_y)

    def draw_transparent_background(self, painter):
        # 背景框位置基于传入的x、y坐标
        painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.bg_square_x, self.bg_square_y, self.bg_square_size, self.bg_square_size)

    def draw_throttle_axis(self, painter, value):
        # 所有坐标基于背景框左上角（bg_square_x, bg_square_y）计算
        base_x = self.bg_square_x + 20  # 背景框内x偏移
        base_y = self.bg_square_y + 160  # 背景框内y偏移
        line_height = 150

        # 主竖线
        pen = QPen(QColor(255, 0, 0, 128), 2)
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x, base_y - line_height)

        # 辅助横线
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(base_x - 7, base_y, base_x + 7, base_y)
        painter.drawLine(base_x - 7, base_y - line_height * 0.75, base_x + 7, base_y - line_height * 0.75)

        # 指示器横线
        indicator_y = base_y - value * line_height
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(base_x - 10, indicator_y, base_x + 10, indicator_y)

    def draw_rudder_axis(self, painter, value):
        # 所有坐标基于背景框左上角计算
        base_x = self.bg_square_x + 45  # 背景框内x偏移
        base_y = self.bg_square_y + 160  # 背景框内y偏移
        line_length = 100

        # 主横线
        pen = QPen(QColor(255, 0, 0, 128), 2)
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x + line_length, base_y)

        # 辅助竖线
        pen.setWidth(1)
        painter.setPen(pen)
        mid_x = base_x + line_length / 2
        painter.drawLine(mid_x, base_y - 5, mid_x, base_y + 5)

        # 指示器竖线
        indicator_x = base_x + value * line_length
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(indicator_x, base_y - 5, indicator_x, base_y + 5)

    def draw_quadrant_cross(self, painter, x_value, y_value):
        # 所有坐标基于背景框左上角计算
        center_x = self.bg_square_x + 95  # 背景框内x偏移（中心）
        center_y = self.bg_square_y + 85  # 背景框内y偏移（中心）
        cross_size = 60

        # 十字线
        pen = QPen(QColor(255, 0, 0, 128), 2)
        painter.setPen(pen)
        painter.drawLine(center_x - cross_size, center_y, center_x + cross_size, center_y)
        painter.drawLine(center_x, center_y - cross_size, center_x, center_y + cross_size)

        # 菱形位置计算
        ball_x = center_x + (x_value - 0.5) * 2 * cross_size
        ball_y = center_y + (y_value - 0.5) * 2 * cross_size
        # 菱形顶点
        diamond_points = [
            QPointF(ball_x, ball_y - 6.5),
            QPointF(ball_x + 5, ball_y),
            QPointF(ball_x, ball_y + 6.5),
            QPointF(ball_x - 5, ball_y)
        ]

        # 绘制菱形
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(QPolygonF(diamond_points))

    def show_overlay(self, show: bool):
        self.setVisible(show)
        # 控制定时器
        if show:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()
