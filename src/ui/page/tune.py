from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import i18n
from data.config import ConfigData
from data.flight import FlightData
from ui.window.axis import JoyAxisWindow


class TunePage(QWidget):
    def __init__(self, config: ConfigData, flight: FlightData, parent=None):
        super().__init__(parent)

        self.config = config
        self.flight = flight

        # Create the main layout
        self.axisTunePageLayout = QVBoxLayout(self)
        self.axisTunePageLayout.setSpacing(10)
        self.axisTunePageLayout.setContentsMargins(0, 0, 0, 0)

        # Create labels
        self.x_label = QLabel()
        self.y_label = QLabel()
        self.z_label = QLabel()
        self.rx_label = QLabel()
        self.ry_label = QLabel()
        self.rz_label = QLabel()

        # X Axis
        x_axis_layout = QHBoxLayout()
        x_axis_layout.setSpacing(10)
        x_axis_layout.addWidget(self.x_label)
        x_axis_layout.addStretch()
        self.xAxisButton = QPushButton()
        self.xAxisButton.clicked.connect(lambda: self.open_axis_window('x'))
        x_axis_layout.addWidget(self.xAxisButton)
        self.axisTunePageLayout.addLayout(x_axis_layout)

        # Y Axis
        y_axis_layout = QHBoxLayout()
        y_axis_layout.setSpacing(10)
        y_axis_layout.addWidget(self.y_label)
        y_axis_layout.addStretch()
        self.yAxisButton = QPushButton()
        self.yAxisButton.clicked.connect(lambda: self.open_axis_window('y'))
        y_axis_layout.addWidget(self.yAxisButton)
        self.axisTunePageLayout.addLayout(y_axis_layout)

        # Z Axis
        z_axis_layout = QHBoxLayout()
        z_axis_layout.setSpacing(10)
        z_axis_layout.addWidget(self.z_label)
        z_axis_layout.addStretch()
        self.zAxisButton = QPushButton()
        self.zAxisButton.clicked.connect(lambda: self.open_axis_window('z'))
        z_axis_layout.addWidget(self.zAxisButton)
        self.axisTunePageLayout.addLayout(z_axis_layout)

        # RX Axis
        rx_axis_layout = QHBoxLayout()
        rx_axis_layout.setSpacing(10)
        rx_axis_layout.addWidget(self.rx_label)
        rx_axis_layout.addStretch()
        self.rxAxisButton = QPushButton()
        self.rxAxisButton.clicked.connect(lambda: self.open_axis_window('rx'))
        rx_axis_layout.addWidget(self.rxAxisButton)
        self.axisTunePageLayout.addLayout(rx_axis_layout)

        # RY Axis
        ry_axis_layout = QHBoxLayout()
        ry_axis_layout.setSpacing(10)
        ry_axis_layout.addWidget(self.ry_label)
        ry_axis_layout.addStretch()
        self.ryAxisButton = QPushButton()
        self.ryAxisButton.clicked.connect(lambda: self.open_axis_window('ry'))
        ry_axis_layout.addWidget(self.ryAxisButton)
        self.axisTunePageLayout.addLayout(ry_axis_layout)

        # RZ Axis
        rz_axis_layout = QHBoxLayout()
        rz_axis_layout.setSpacing(10)
        rz_axis_layout.addWidget(self.rz_label)
        rz_axis_layout.addStretch()
        self.rzAxisButton = QPushButton()
        self.rzAxisButton.clicked.connect(lambda: self.open_axis_window('rz'))
        rz_axis_layout.addWidget(self.rzAxisButton)
        self.axisTunePageLayout.addLayout(rz_axis_layout)

        # Initialize UI texts
        self.retranslate_ui()

        self.axisTunePageLayout.addStretch()

    def retranslate_ui(self):
        self.x_label.setText(i18n.t('JoyAxis', axis='X'))
        self.y_label.setText(i18n.t('JoyAxis', axis='Y'))
        self.z_label.setText(i18n.t('JoyAxis', axis='Z'))
        self.rx_label.setText(i18n.t('JoyAxis', axis='RX'))
        self.ry_label.setText(i18n.t('JoyAxis', axis='RY'))
        self.rz_label.setText(i18n.t('JoyAxis', axis='RZ'))
        self.xAxisButton.setText(i18n.t('Modify'))
        self.yAxisButton.setText(i18n.t('Modify'))
        self.zAxisButton.setText(i18n.t('Modify'))
        self.rxAxisButton.setText(i18n.t('Modify'))
        self.ryAxisButton.setText(i18n.t('Modify'))
        self.rzAxisButton.setText(i18n.t('Modify'))

    def open_axis_window(self, axis_name: str):
        window = JoyAxisWindow(axis_name, self.flight, self)
        window.show()
