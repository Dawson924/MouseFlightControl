from PySide2.QtCore import QPointF, Qt, QTimer
from PySide2.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide2.QtWidgets import QApplication, QWidget


class IndicatorWindow(QWidget):
    def __init__(
        self, parent, x, y, bg_color, line_color, bg_square_size=200, scale=1.0
    ):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.X11BypassWindowManagerHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.target_throttle = 0.0
        self.target_rudder = 0.5
        self.target_x = 0.5
        self.target_y = 0.5
        self.current_throttle = self.target_throttle
        self.current_rudder = self.target_rudder
        self.current_x = self.target_x
        self.current_y = self.target_y

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(4)
        self.refresh_timer.timeout.connect(self._smooth_update_and_paint)
        self.refresh_timer.start()

        self.screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(self.screen_rect)
        self.bg_square_size = bg_square_size * scale
        if x < 0:
            self.bg_square_x = self.screen_rect.width() - self.bg_square_size - abs(x)
        else:
            self.bg_square_x = x
        if y < 0:
            self.bg_square_y = self.screen_rect.height() - self.bg_square_size - abs(y)
        else:
            self.bg_square_y = y

        # 线条宽度基于背景尺寸比例计算
        self.base_line = 0.006 * self.bg_square_size
        self.shifted_line = 0.019 * self.bg_square_size

        self._background_color = QColor(*bg_color)
        self._foreground_color = QColor(*line_color)

    def set_background_color(self, r: int, g: int, b: int, a: int):
        """设置背景颜色，参数为RGBA值（0-255）"""
        self._background_color = QColor(r, g, b, a)
        self.update()

    def set_foreground_color(self, r: int, g: int, b: int, a: int):
        """设置前景线段颜色，参数为RGBA值（0-255）"""
        self._foreground_color = QColor(r, g, b, a)
        self.update()

    def set_throttle_value(self, value):
        self.target_throttle = max(0.0, min(1.0, value))

    def set_rudder_value(self, value):
        self.target_rudder = max(0.0, min(1.0, value))

    def set_xy_values(self, x_value, y_value):
        self.target_x = max(0.0, min(1.0, x_value))
        self.target_y = max(0.0, min(1.0, y_value))

    def set_position(self, x, y):
        self.bg_square_x = x
        self.bg_square_y = y
        self.update()

    def set_bg_size(self, size):
        self.bg_square_size = size
        self.base_line = 0.006 * self.bg_square_size
        self.shifted_line = 0.019 * self.bg_square_size
        self.update()

    def _smooth_update_and_paint(self):
        smooth_factor = 0.15

        if abs(self.current_throttle - self.target_throttle) > 0.001:
            self.current_throttle += (
                self.target_throttle - self.current_throttle
            ) * smooth_factor
        else:
            self.current_throttle = self.target_throttle

        if abs(self.current_rudder - self.target_rudder) > 0.001:
            self.current_rudder += (
                self.target_rudder - self.current_rudder
            ) * smooth_factor
        else:
            self.current_rudder = self.target_rudder

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
        self.draw_throttle_axis(painter, self.current_throttle)
        self.draw_rudder_axis(painter, self.current_rudder)
        self.draw_quadrant_cross(painter, self.current_x, self.current_y)

    def draw_transparent_background(self, painter):
        painter.setBrush(QBrush(self._background_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(
            self.bg_square_x, self.bg_square_y, self.bg_square_size, self.bg_square_size
        )

    def draw_throttle_axis(self, painter, value):
        base_x_ratio = 0.1
        base_y_ratio = 0.95
        line_height_ratio = 0.8625
        aux_line_offset_ratio = 0.025
        indicator_offset_ratio = 0.05

        base_x = self.bg_square_x + base_x_ratio * self.bg_square_size
        base_y = self.bg_square_y + base_y_ratio * self.bg_square_size
        line_height = line_height_ratio * self.bg_square_size
        aux_offset = aux_line_offset_ratio * self.bg_square_size
        indicator_offset = indicator_offset_ratio * self.bg_square_size

        fg_r = self._foreground_color.red()
        fg_g = self._foreground_color.green()
        fg_b = self._foreground_color.blue()
        aux_alpha = self._foreground_color.alpha() // 2

        # 主竖线
        pen = QPen(QColor(fg_r, fg_g, fg_b, aux_alpha), self.base_line)
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x, base_y - line_height)

        # 辅助横线
        pen.setWidth(self.base_line)
        painter.setPen(pen)
        painter.drawLine(base_x - aux_offset, base_y, base_x + aux_offset, base_y)
        painter.drawLine(
            base_x - aux_offset,
            base_y - line_height * 0.75,
            base_x + aux_offset,
            base_y - line_height * 0.75,
        )

        # 指示器横线
        indicator_y = base_y - value * line_height
        pen.setColor(self._foreground_color)
        pen.setWidth(self.shifted_line)
        painter.setPen(pen)
        painter.drawLine(
            base_x - indicator_offset,
            indicator_y,
            base_x + indicator_offset,
            indicator_y,
        )

    # 绘制方向舵轴
    def draw_rudder_axis(self, painter, value):
        # 所有位置基于背景尺寸比例计算
        base_x_ratio = 0.2  # 原40 → 200*0.2
        base_y_ratio = 0.95  # 原190 → 200*0.95
        line_length_ratio = 0.7  # 原140 → 200*0.7
        aux_line_offset_ratio = 0.025  # 原5 → 200*0.025

        base_x = self.bg_square_x + base_x_ratio * self.bg_square_size
        base_y = self.bg_square_y + base_y_ratio * self.bg_square_size
        line_length = line_length_ratio * self.bg_square_size
        aux_offset = aux_line_offset_ratio * self.bg_square_size

        # 提取前景色分量
        fg_r = self._foreground_color.red()
        fg_g = self._foreground_color.green()
        fg_b = self._foreground_color.blue()
        aux_alpha = self._foreground_color.alpha() // 2

        # 主横线
        pen = QPen(QColor(fg_r, fg_g, fg_b, aux_alpha), self.base_line)
        painter.setPen(pen)
        painter.drawLine(base_x, base_y, base_x + line_length, base_y)

        # 辅助竖线
        pen.setWidth(self.base_line)
        painter.setPen(pen)
        mid_x = base_x + line_length / 2
        painter.drawLine(mid_x, base_y - aux_offset, mid_x, base_y + aux_offset)

        # 指示器竖线
        indicator_x = base_x + value * line_length + 0.1
        pen.setColor(self._foreground_color)
        pen.setWidth(self.shifted_line)
        painter.setPen(pen)
        painter.drawLine(
            indicator_x, base_y - aux_offset, indicator_x, base_y + aux_offset
        )

    # 绘制十字象限
    def draw_quadrant_cross(self, painter, x_value, y_value):
        # 所有位置基于背景尺寸比例计算
        center_x_ratio = 0.55  # 原110 → 200*0.55
        center_y_ratio = 0.475  # 原95 → 200*0.475
        cross_size_ratio = 0.4  # 原80 → 200*0.4
        diamond_vert_ratio = 0.0325  # 原6.5 → 200*0.0325
        diamond_horiz_ratio = 0.025  # 原5 → 200*0.025
        diamond_pen_ratio = 0.01  # 原2 → 200*0.01

        center_x = self.bg_square_x + center_x_ratio * self.bg_square_size
        center_y = self.bg_square_y + center_y_ratio * self.bg_square_size
        cross_size = cross_size_ratio * self.bg_square_size
        diamond_vert = diamond_vert_ratio * self.bg_square_size
        diamond_horiz = diamond_horiz_ratio * self.bg_square_size
        diamond_pen = diamond_pen_ratio * self.bg_square_size

        fg_r = self._foreground_color.red()
        fg_g = self._foreground_color.green()
        fg_b = self._foreground_color.blue()
        aux_alpha = self._foreground_color.alpha() // 2

        # 十字线
        pen = QPen(QColor(fg_r, fg_g, fg_b, aux_alpha), self.base_line)
        painter.setPen(pen)
        painter.drawLine(
            center_x - cross_size, center_y, center_x + cross_size, center_y
        )
        painter.drawLine(
            center_x, center_y - cross_size, center_x, center_y + cross_size
        )

        # 菱形指示器
        ball_x = center_x + (x_value - 0.5) * 2 * cross_size
        ball_y = center_y + (y_value - 0.5) * 2 * cross_size
        diamond_points = [
            QPointF(ball_x, ball_y - diamond_vert),
            QPointF(ball_x + diamond_horiz, ball_y),
            QPointF(ball_x, ball_y + diamond_vert),
            QPointF(ball_x - diamond_horiz, ball_y),
        ]

        pen.setColor(self._foreground_color)
        pen.setWidth(diamond_pen)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(QPolygonF(diamond_points))

    def show_overlay(self, show: bool):
        self.setVisible(show)
        if show:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()
