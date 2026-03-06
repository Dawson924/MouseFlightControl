import os
from typing import Dict

from loguru import logger
from PySide2.QtCore import QObject, Qt, QTimer, Signal
from PySide2.QtGui import QPainter, QPainterPath, QPixmap
from PySide2.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import i18n
from data.flight import FlightData
from flightsim.module import FlightSim


class ConnectModel(QObject):
    data_updated = Signal()
    error_occurred = Signal(str)

    def __init__(self, modules: Dict):
        super().__init__()
        self.modules = modules
        self.platforms = {
            FlightSim.DCS: {'name': 'DCS'},
            FlightSim.FS2020: {'name': 'Flight Simulator 2020'},
        }

        self.aircrafts = {FlightSim.DCS: [], FlightSim.FS2020: []}

        for mod_id, data in modules.items():
            dir, module = data
            if 'Manifest' in module:
                mod_id = module['Manifest']['model']
                sim = module['Manifest']['platform']
                name = module['Manifest']['title']
                self.aircrafts[FlightSim(sim)].append(
                    {'key': mod_id, 'name': name, 'image_path': os.path.join(dir, 'bg_image.jpg')}
                )

    def get_platforms(self):
        return [(key, info['name']) for key, info in self.platforms.items()]

    def get_platform(self, platform):
        return self.platforms.get(platform, {}).get('name', '')

    def connect_flight(self, platform):
        if platform not in self.platforms:
            self.error_occurred.emit(f"Platform '{platform}' does not exist")
            return False
        try:
            self.data_updated.emit()
            return True
        except Exception as e:
            self.error_occurred.emit(f'Failed to connect to platform: {str(e)}')
            self.data_updated.emit()
            return False

    def disconnect_flight(self, platform):
        if platform not in self.platforms:
            self.error_occurred.emit(f"Platform '{platform}' does not exist")
            return False
        try:
            self.data_updated.emit()
            return True
        except Exception as e:
            self.error_occurred.emit(f'Failed to disconnect platform: {str(e)}')
            self.data_updated.emit()
            return False

    def get_aircraft_modules(self, platform):
        return self.aircrafts.get(platform, [])

    def get_module(self, platform, module_id):
        for module in self.get_aircraft_modules(platform):
            if module['key'] == module_id:
                return module
        return {}


class ImageLabel(QLabel):
    def __init__(self, parent=None, radius=4):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = QPixmap()
        self.radius = radius

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        if self._pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.contentsRect()

        scaled_pixmap = self._pixmap.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        x = (rect.width() - scaled_pixmap.width()) // 2
        y = (rect.height() - scaled_pixmap.height()) // 2

        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        painter.drawPixmap(x, y, scaled_pixmap)

        # rect = self.contentsRect()

        # scaled_pixmap = self._pixmap.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # x = (rect.width() - scaled_pixmap.width()) // 2
        # y = (rect.height() - scaled_pixmap.height()) // 2

        # path = QPainterPath()
        # path.moveTo(rect.left(), rect.bottom())
        # path.lineTo(rect.right(), rect.bottom())
        # path.lineTo(rect.right(), rect.top() + self.radius)
        # path.arcTo(rect.right() - self.radius, rect.top(), self.radius, self.radius, 0.0, 90.0)
        # path.lineTo(rect.left() + self.radius, rect.top())
        # path.arcTo(rect.left(), rect.top(), self.radius, self.radius, 90.0, 90.0)
        # path.lineTo(rect.left(), rect.bottom())
        # path.closeSubpath()

        # painter.setClipPath(path)
        # painter.drawPixmap(x, y, scaled_pixmap)


class ImageCard(QFrame):
    clicked = Signal(str)

    def __init__(self, module_id, module_name, parent=None):
        super().__init__(parent)
        self.module_id = module_id
        self.module_name = module_name

        self.setStyleSheet("""
            ImageCard {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            ImageCard:hover {
                background-color: #eef2f7;
                border-color: #dee2e6;
            }
        """)

        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_container = QWidget(self)
        self.image_container.setMinimumHeight(130)
        self.image_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_image_label = ImageLabel(self.image_container, radius=8)
        self.bg_image_label.setMinimumHeight(130)
        container_layout.addWidget(self.bg_image_label)

        self.name_label = QLabel(module_name, self.image_container)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        layout.addWidget(self.image_container)

        self.setCursor(Qt.PointingHandCursor)

        self._has_image = False
        self._current_alpha = 180
        self._target_alpha = 180
        self._transition_timer = QTimer(self)
        self._transition_timer.setInterval(16)
        self._transition_timer.timeout.connect(self._on_transition_tick)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.image_container.width()
        h = self.name_label.sizeHint().height()
        container_h = self.image_container.height()
        self.name_label.setGeometry(0, container_h - h, w, h)

    def _name_label_stylesheet(self, alpha):
        return f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: #d0d0d0;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 transparent, stop:1 rgba(0, 0, 0, {alpha}));
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 18px 8px 6px 8px;
            }}
        """

    def _start_transition(self, target_alpha):
        self._target_alpha = target_alpha
        if not self._transition_timer.isActive():
            self._transition_timer.start()

    def _on_transition_tick(self):
        step = 8
        if self._current_alpha < self._target_alpha:
            self._current_alpha = min(self._current_alpha + step, self._target_alpha)
        elif self._current_alpha > self._target_alpha:
            self._current_alpha = max(self._current_alpha - step, self._target_alpha)
        self.name_label.setStyleSheet(self._name_label_stylesheet(self._current_alpha))
        if self._current_alpha == self._target_alpha:
            self._transition_timer.stop()

    def enterEvent(self, event):
        if self._has_image:
            self._start_transition(230)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._has_image:
            self._start_transition(180)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.module_id)
        super().mousePressEvent(event)

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self._has_image = True
            self.bg_image_label.setPixmap(pixmap)
            self.bg_image_label.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                    padding: 0px;
                }
            """)
            self.name_label.setStyleSheet(self._name_label_stylesheet(self._current_alpha))
        else:
            self._has_image = False
            self.bg_image_label.setPixmap(QPixmap())
            self.bg_image_label.setStyleSheet("""
                QLabel {
                    background-color: #dcdcdc;
                    border-radius: 8px;
                    padding: 0px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 500;
                    color: #2c3e50;
                    background-color: transparent;
                    margin-left: 4px;
                    padding-bottom: 6px;
                }
            """)


class ConnectView(QWidget):
    connect_requested = Signal(str)
    disconnect_requested = Signal(str)
    platform_selected = Signal(str)
    module_clicked = Signal(str, str)
    state_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.connectLayout = QVBoxLayout(self)
        self.connectLayout.setSpacing(10)
        self.connectLayout.setContentsMargins(0, 0, 0, 0)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        self.flightSimLabel = QLabel(i18n.t('FlightSim'))
        self.flightSimLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
            }
        """)
        h_layout.addWidget(self.flightSimLabel)
        self.flightSimSelect = QComboBox()
        size_policy = self.flightSimSelect.sizePolicy()
        size_policy.setVerticalPolicy(size_policy.Fixed)
        self.flightSimSelect.setSizePolicy(size_policy)
        self.flightSimSelect.setMinimumWidth(200)
        self.flightSimSelect.currentIndexChanged.connect(self._on_platform_changed)
        h_layout.addWidget(self.flightSimSelect)
        self.connectLayout.addLayout(h_layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c4cc;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #909399;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)

        self.gallery_container = QWidget()
        self.gallery_layout = QVBoxLayout(self.gallery_container)
        self.gallery_layout.setSpacing(8)
        self.gallery_layout.setContentsMargins(0, 0, 4, 0)
        self.gallery_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.gallery_container)

        self.connectLayout.addWidget(self.scroll_area)

        self.module_cards = {}
        self._block_platform_signal = False

    def bind(self, vm: 'ConnectViewModel'):
        vm.platforms_changed.connect(self._populate_platforms)
        vm.modules_changed.connect(self._load_modules)
        vm.state_changed.connect(self._update)

        self.connect_requested.connect(vm.handle_connect)
        self.disconnect_requested.connect(vm.handle_disconnect)
        self.platform_selected.connect(vm.select_platform)
        self.module_clicked.connect(vm.handle_module_clicked)

        vm.initialize()

    def _update(self):
        self.state_changed.emit()

    def _populate_platforms(self, platforms):
        self._block_platform_signal = True
        self.flightSimSelect.clear()
        for key, name in platforms:
            self.flightSimSelect.addItem(name, key)
        self._block_platform_signal = False

    def _load_modules(self, modules):
        for card in self.module_cards.values():
            card.deleteLater()
        self.module_cards.clear()

        for module in modules:
            card = ImageCard(module['key'], module['name'])
            card.set_background_image(module['image_path'])
            card.clicked.connect(lambda key=module['key']: self._on_module_clicked(key))
            self.module_cards[module['key']] = card
            self.gallery_layout.addWidget(card)

    def _on_platform_changed(self):
        if self._block_platform_signal:
            return
        platform = self.flightSimSelect.currentData()
        if platform is not None:
            self.platform_selected.emit(platform)

    def _on_module_clicked(self, module_id):
        platform = self.flightSimSelect.currentData()
        if platform is not None:
            self.module_clicked.emit(platform, module_id)

    def get_selected_platform(self):
        return self.flightSimSelect.currentData()

    def on_connect(self):
        platform = self.get_selected_platform()
        if not platform:
            self.show_message('Error', 'Please select a flight simulator platform first', is_error=True)
            return
        self.connect_requested.emit(platform)

    def on_disconnect(self):
        platform = self.get_selected_platform()
        if not platform:
            self.show_message('Error', 'Please select a flight simulator platform first', is_error=True)
            return
        self.disconnect_requested.emit(platform)


class ConnectViewModel(QObject):
    platforms_changed = Signal(list)
    modules_changed = Signal(list)
    state_changed = Signal()

    def __init__(self, model: ConnectModel, flight: FlightData):
        super().__init__()
        self.model = model
        self.flight = flight
        self._current_platform = None

        self.model.error_occurred.connect(self._on_error)
        self.model.data_updated.connect(self._on_data_updated)

    def initialize(self):
        platforms = self.model.get_platforms()
        self.platforms_changed.emit(platforms)
        if platforms:
            self.select_platform(platforms[0][0])

    def select_platform(self, platform):
        self._current_platform = platform
        modules = self.model.get_aircraft_modules(platform)
        self.modules_changed.emit(modules)

    def handle_module_clicked(self, platform: str, module_id: str):
        module = self.model.get_module(platform, module_id)
        if not module:
            self._on_error(f"Module '{module_id}' not found")
            return
        self.flight['Connect']['model'] = module_id
        module = self.model.modules[module_id][1]
        self.flight['Input'] = module['Data']
        self.state_changed.emit()

    def handle_connect(self, platform):
        success = self.model.connect_flight(platform)
        if success:
            platform_name = self.model.get_platform(platform)
            self.state_updated.emit('Success', f'{platform_name} connected successfully', False)

    def handle_disconnect(self, platform):
        success = self.model.disconnect_flight(platform)
        if success:
            platform_name = self.model.get_platform(platform)
            self.state_updated.emit('Success', f'{platform_name} disconnected successfully', False)

    def _on_error(self, error_msg):
        self.state_updated.emit('Error', error_msg, True)

    def _on_data_updated(self):
        if self._current_platform is not None:
            self.select_platform(self._current_platform)