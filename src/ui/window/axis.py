from PySide2.QtCore import QPointF, Qt, Slot
from PySide2.QtGui import QBrush, QColor, QPainter, QPen
from PySide2.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from common.axis import AxisName
from data.flight import FlightData
from type.filter import Filter


class JoyAxisChart(QWidget):
    def __init__(self, curve: Filter, square_length=400, curve_color=Qt.red, axis_color=Qt.gray, parent=None):
        super().__init__(parent)
        # Core parameters
        self.curvature = curve.curvature
        self.dead_zone = curve.deadzone
        self.axis_boundary = 1.0

        # Style parameters
        self.square_length = square_length
        self.curve_color = QColor(curve_color)
        self.axis_color = QColor(axis_color)

        self.setFixedSize(self.square_length, self.square_length)

    def set_curvature(self, value):
        self.curvature = value / 100.0
        self.update()

    def set_dead_zone(self, value):
        self.dead_zone = value / 100.0
        self.update()

    def set_axis_boundary(self, value):
        self.axis_boundary = max(0.1, value / 100.0)
        self.update()

    def reset_parameters(self):
        self.curvature = 0.0
        self.dead_zone = 0.0
        self.axis_boundary = 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        center_x = self.square_length // 2
        center_y = self.square_length // 2
        max_side = self.square_length // 2
        actual_side = int(max_side * self.axis_boundary)

        square_pen = QPen(Qt.black, 1.5)
        painter.setPen(square_pen)
        painter.drawRect(center_x - max_side, center_y - max_side, 2 * max_side, 2 * max_side)

        axis_pen = QPen(self.axis_color, 0.8, Qt.DashLine)
        painter.setPen(axis_pen)
        painter.drawLine(center_x - actual_side, center_y, center_x + actual_side, center_y)
        painter.drawLine(center_x, center_y - actual_side, center_x, center_y + actual_side)

        if self.dead_zone > 0.0:
            dead_zone_radius = int(actual_side * self.dead_zone)
            dead_zone_pen = QPen(Qt.yellow, 0.8, Qt.DotLine)
            dead_zone_brush = QBrush(QColor(255, 255, 0, 30))
            painter.setPen(dead_zone_pen)
            painter.setBrush(dead_zone_brush)
            painter.drawEllipse(
                center_x - dead_zone_radius,
                center_y - dead_zone_radius,
                2 * dead_zone_radius,
                2 * dead_zone_radius,
            )

        curve_pen = QPen(self.curve_color, 1.8)
        curve_pen.setCapStyle(Qt.RoundCap)
        curve_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(curve_pen)
        curve_points = []

        step = max(1, actual_side // 500)
        for x_pixel in range(-actual_side, actual_side + 1, step):
            x_norm = x_pixel / actual_side
            dead_zone = self.dead_zone
            if abs(x_norm) < dead_zone:
                x = 0.0
            else:
                sign = 1 if x_norm > 0 else -1
                denominator = 1 - dead_zone
                if denominator == 0:
                    x = sign
                else:
                    x = (x_norm - dead_zone * sign) / denominator

            c = self.curvature
            c_abs = abs(c)
            n = 3
            if c >= 0:
                cubic = x * (1 - c_abs) + (x**n) * c_abs
                y = cubic * (1 - c_abs) + (cubic**n) * c_abs
            else:
                sign = 1 if x >= 0 else -1
                x_abs = abs(x)
                comp1 = x * (1 - c_abs) + sign * (1 - (1 - x_abs) ** n) * c_abs
                comp1_abs = abs(comp1)
                sign2 = 1 if comp1 >= 0 else -1
                comp2 = sign2 * (1 - (1 - comp1_abs) ** n)
                y = comp1 * (1 - c_abs) + comp2 * c_abs

            y_norm = max(min(y, 1.0), -1.0)

            x = center_x + x_pixel
            y = center_y - (y_norm * actual_side)
            curve_points.append(QPointF(x, y))

        # Draw curve
        if len(curve_points) > 1:
            painter.drawPolyline(curve_points)

        # Draw markers
        # marker_brush = QBrush(Qt.blue)
        # painter.setBrush(marker_brush)
        # painter.setPen(Qt.NoPen)
        # painter.drawEllipse(center_x - actual_side - 2, center_y - 2, 4, 4)
        # painter.drawEllipse(center_x - 2, center_y - 2, 4, 4)
        # painter.drawEllipse(center_x + actual_side - 2, center_y - 2, 4, 4)

        # Curve endpoints marker
        if len(curve_points) > 0:
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(curve_points[0], 3, 3)
            painter.drawEllipse(curve_points[-1], 3, 3)


class JoyAxisWindow(QMainWindow):
    def __init__(self, axis: AxisName, flightinput: FlightData, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Configure - Axis {axis.upper()}')
        self.setFixedSize(750, 465)
        self.axis = axis
        self.flightinput = flightinput
        self.filter = flightinput.get_filter(axis)
        self.curve = JoyAxisChart(self.filter)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.curve)
        top_layout.addWidget(self._create_parameter_panel())
        main_layout.addLayout(top_layout)

        # Button layout
        button_layout = self._create_button_bar()
        main_layout.addLayout(button_layout)

    def _create_parameter_panel(self):
        panel = QGroupBox('Parameter Adjustment')
        layout = QVBoxLayout(panel)

        # Curvature control
        curvature_group = QVBoxLayout()
        self.curvature_label = QLabel(f'Curvature: {self.curve.curvature:.0%}')
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setRange(-100, 100)
        self.curvature_slider.setValue(self.filter.curvature)
        self.curvature_slider.valueChanged.connect(self.on_curvature_changed)

        curvature_group.addWidget(self.curvature_label)
        curvature_group.addWidget(self.curvature_slider)

        # Dead zone control
        deadzone_group = QVBoxLayout()
        self.deadzone_label = QLabel(f'Dead Zone: {self.curve.dead_zone:.0%}')
        self.deadzone_slider = QSlider(Qt.Horizontal)
        self.deadzone_slider.setRange(0, 100)
        self.deadzone_slider.setValue(self.filter.deadzone)
        self.deadzone_slider.valueChanged.connect(self.on_deadzone_changed)

        deadzone_group.addWidget(self.deadzone_label)
        deadzone_group.addWidget(self.deadzone_slider)

        # Axis boundary control
        boundary_group = QVBoxLayout()
        self.boundary_label = QLabel(f'Axis Boundary: {self.curve.axis_boundary:.2f}')
        self.boundary_slider = QSlider(Qt.Horizontal)
        self.boundary_slider.setRange(10, 100)
        self.boundary_slider.setValue(100)
        self.boundary_slider.valueChanged.connect(self.on_boundary_changed)

        boundary_group.addWidget(self.boundary_label)
        boundary_group.addWidget(self.boundary_slider)

        layout.addLayout(curvature_group)
        layout.addLayout(deadzone_group)
        layout.addLayout(boundary_group)
        layout.addStretch()

        return panel

    def _create_button_bar(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignRight)

        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.close)

        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self.on_reset_clicked)

        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.on_save_clicked)

        layout.addWidget(cancel_btn)
        layout.addSpacing(10)
        layout.addWidget(reset_btn)
        layout.addSpacing(10)
        layout.addWidget(save_btn)

        return layout

    @Slot(int)
    def on_curvature_changed(self, value):
        self.curve.set_curvature(value)
        self.curvature_label.setText(f'Curvature: {self.curve.curvature:.0%}')

    @Slot(int)
    def on_deadzone_changed(self, value):
        self.curve.set_dead_zone(value)
        self.deadzone_label.setText(f'Dead Zone: {self.curve.dead_zone:.0%}')

    @Slot(int)
    def on_boundary_changed(self, value):
        self.curve.set_axis_boundary(value)
        self.boundary_label.setText(f'Axis Boundary: {self.curve.axis_boundary:.2f}')

    @Slot()
    def on_reset_clicked(self):
        self.curve.reset_parameters()
        self.curvature_slider.setValue(0)
        self.deadzone_slider.setValue(0)
        self.boundary_slider.setValue(100)
        self.curvature_label.setText(f'Curvature: {self.curve.curvature:.2f}')
        self.deadzone_label.setText(f'Dead Zone: {self.curve.dead_zone:.0%}')
        self.boundary_label.setText(f'Axis Boundary: {self.curve.axis_boundary:.2f}')

    @Slot()
    def on_save_clicked(self):
        self.flightinput.set_filter(self.axis, Filter(False, self.curve.curvature, self.curve.dead_zone))
        self.close()
