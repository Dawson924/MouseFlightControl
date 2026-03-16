from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

import i18n
from data.config import ConfigData
from data.flight import FlightData
from ui.page import AbstractPage


class ControlsPage(AbstractPage):
    def __init__(self, config: ConfigData, flight: FlightData, parent=None):
        super().__init__(config, flight, parent)

        self.controlsPageLayout = self.page_layout

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
        self.mouse_speed.valueChanged.connect(lambda v: self.set_config('mouse_speed', v))
        sensitivity_layout.addWidget(self.mouse_speed)
        self.ui_elements.update({'mouse_speed': [int]})

        # Slider value label
        self.mouse_speed_status_label = QLabel('5')
        self.mouse_speed_status_label.setStyleSheet('color: #505050; font-size: 9pt; min-width: 30px;')
        sensitivity_layout.addWidget(self.mouse_speed_status_label)

        self.controlsPageLayout.addLayout(sensitivity_layout)

        # Toggle enabled key
        toggle_control_layout = QHBoxLayout()
        toggle_control_layout.setSpacing(10)
        self.key_toggle_label = QLabel()
        toggle_control_layout.addWidget(self.key_toggle_label)
        toggle_control_layout.addStretch()
        self.key_toggle = QLineEdit()
        self.key_toggle.textChanged.connect(lambda t: self.set_config('key_toggle', t))
        toggle_control_layout.addWidget(self.key_toggle)
        self.controlsPageLayout.addLayout(toggle_control_layout)
        self.ui_elements.update({'key_toggle': [str]})

        # Center control key
        center_control_layout = QHBoxLayout()
        center_control_layout.setSpacing(10)
        self.key_center_label = QLabel()
        center_control_layout.addWidget(self.key_center_label)
        center_control_layout.addStretch()
        self.key_center = QLineEdit()
        self.key_center.textChanged.connect(lambda t: self.set_config('key_center', t))
        center_control_layout.addWidget(self.key_center)
        self.controlsPageLayout.addLayout(center_control_layout)
        self.ui_elements.update({'key_center': [str]})

        # Enable freecam key
        enable_freecam_layout = QHBoxLayout()
        enable_freecam_layout.setSpacing(10)
        self.key_freecam_label = QLabel()
        enable_freecam_layout.addWidget(self.key_freecam_label)
        enable_freecam_layout.addStretch()
        self.key_freecam = QLineEdit()
        self.key_freecam.textChanged.connect(lambda t: self.set_config('key_freecam', t))
        enable_freecam_layout.addWidget(self.key_freecam)
        self.controlsPageLayout.addLayout(enable_freecam_layout)
        self.ui_elements.update({'key_freecam': [str]})

        # View center key
        view_center_layout = QHBoxLayout()
        view_center_layout.setSpacing(10)
        self.key_view_center_label = QLabel()
        view_center_layout.addWidget(self.key_view_center_label)
        view_center_layout.addStretch()
        self.key_view_center = QLineEdit()
        self.key_view_center.textChanged.connect(lambda t: self.set_config('key_view_center', t))
        view_center_layout.addWidget(self.key_view_center)
        self.controlsPageLayout.addLayout(view_center_layout)
        self.ui_elements.update({'key_view_center': [str]})

        # Camera FOV
        camera_fov_layout = QHBoxLayout()
        camera_fov_layout.setSpacing(10)
        self.camera_fov_label = QLabel()
        camera_fov_layout.addWidget(self.camera_fov_label)
        camera_fov_layout.addStretch()
        self.camera_fov = QSpinBox()
        self.camera_fov.setMinimum(40)
        self.camera_fov.setMaximum(160)
        self.camera_fov.valueChanged.connect(lambda v: self.set_flight_data('camera_fov', v))
        camera_fov_layout.addWidget(self.camera_fov)
        self.controlsPageLayout.addLayout(camera_fov_layout)
        self.ui_elements.update({'camera_fov': [int]})

        # Taxi mode key
        taxi_mode_layout = QHBoxLayout()
        taxi_mode_layout.setSpacing(10)
        self.key_taxi_label = QLabel()
        taxi_mode_layout.addWidget(self.key_taxi_label)
        taxi_mode_layout.addStretch()
        self.key_taxi = QLineEdit()
        self.key_taxi.textChanged.connect(lambda t: self.set_config('key_taxi', t))
        taxi_mode_layout.addWidget(self.key_taxi)
        self.controlsPageLayout.addLayout(taxi_mode_layout)
        self.ui_elements.update({'key_taxi': [str]})

        self.controlsPageLayout.addStretch()

        self.update_states()
        self.retranslate_ui()

    def set_mouse_speed(self, speed):
        self.mouse_speed.setValue(speed)
        self.mouse_speed_status_label.setText(i18n.t('CurrentValue') + f': {str(speed)}')

    def retranslate_ui(self):
        self.mouse_speed_label.setText(i18n.t('Sensitive'))
        self.mouse_speed_status_label.setText(i18n.t('CurrentValue', value=self.mouse_speed.value()))
        self.key_toggle_label.setText(i18n.t('ToggleEnabled'))
        self.key_center_label.setText(i18n.t('CenterControl'))
        self.key_freecam_label.setText(i18n.t('EnableFreecam'))
        self.key_view_center_label.setText(i18n.t('ViewCenter'))
        self.camera_fov_label.setText(i18n.t('CameraFov'))
        self.key_taxi_label.setText(i18n.t('TaxiMode'))
