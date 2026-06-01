from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
)

import i18n
from data.config import Config
from data.flight import FlightInput
from lib.screen import ScreenGeometry
from ui.factory import WidgetFactory
from ui.page import AbstractPage
from ui.widgets import SpinBox


class ControlsPage(AbstractPage):
    def __init__(self, win: ScreenGeometry, config: Config, flight: FlightInput, parent=None):
        super().__init__(win, config, flight, parent)

        self.controlsLayout = self.page_layout

        self._setup_mouse_speed()

        controls_spec = {k: v for k, v in Config.SPEC['Controls'].items() if k != 'mouse_speed'}
        self._widgets = WidgetFactory.populate_from_spec(self.controlsLayout, controls_spec, self.set_config, self)

        for field_name in self._widgets:
            self.ui_elements.update(
                {field_name: [Config.SPEC['Controls'][field_name]['type']]}
            )  # E.g. { 'camera_fov': [int] }

        self._setup_camera_fov()

        WidgetFactory.add_stretch(self.controlsLayout)

        self.update_states()
        self.retranslate_ui()

    def _setup_mouse_speed(self):
        sensitivity_layout = QVBoxLayout()
        sensitivity_layout.setSpacing(5)

        self.mouse_speed_label = QLabel()
        self.mouse_speed_label.setStyleSheet('color: #000000;')
        sensitivity_layout.addWidget(self.mouse_speed_label)

        self.mouse_speed = QSlider(Qt.Horizontal)
        self.mouse_speed.setMinimum(1)
        self.mouse_speed.setMaximum(20)
        self.mouse_speed.setTickPosition(QSlider.TicksBelow)
        self.mouse_speed.setTickInterval(1)
        self.mouse_speed.valueChanged.connect(self.on_speed_changed)
        sensitivity_layout.addWidget(self.mouse_speed)
        self.ui_elements.update({'mouse_speed': [int]})

        self.mouse_speed_status_label = QLabel('5')
        self.mouse_speed_status_label.setStyleSheet('color: #505050; font-size: 9pt; min-width: 30px;')
        sensitivity_layout.addWidget(self.mouse_speed_status_label)

        self.controlsLayout.addLayout(sensitivity_layout)

    def _setup_camera_fov(self):
        camera_fov_layout = QHBoxLayout()
        camera_fov_layout.setSpacing(10)
        self.camera_fov_label = QLabel()
        camera_fov_layout.addWidget(self.camera_fov_label)
        camera_fov_layout.addStretch()
        self.camera_fov = SpinBox()
        self.camera_fov.setMinimum(40)
        self.camera_fov.setMaximum(160)
        self.camera_fov.valueChanged.connect(lambda v: self.set_flight_data('camera_fov', v))
        camera_fov_layout.addWidget(self.camera_fov)
        self.controlsLayout.addLayout(camera_fov_layout)
        self.ui_elements.update({'camera_fov': [int]})

    def on_speed_changed(self, speed):
        self.config.set('mouse_speed', speed)
        self.mouse_speed_status_label.setText(i18n.t('CurrentValue', value=str(speed)))

    def retranslate_ui(self):
        self.mouse_speed_label.setText(i18n.t('Sensitive'))
        self.mouse_speed_status_label.setText(i18n.t('CurrentValue', value=self.mouse_speed.value()))
        WidgetFactory.retranslate_from_spec(Config.SPEC['Controls'], self)
        self.camera_fov_label.setText(i18n.t('CameraFov'))

    def update_ui(self):
        self.update_states()
