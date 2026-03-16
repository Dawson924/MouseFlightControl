import os
from typing import Dict

from PySide2.QtCore import Qt, QTimer, Signal
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
from data.config import ConfigData
from data.flight import FlightData
from flightsim.module import FlightSim, ModuleData

from . import AbstractPage


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

    def _linear_gradient(self, alpha):
        return f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: #d0d0d0;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 transparent, stop:1 rgba(0, 0, 0, {alpha}));
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
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
        self.name_label.setStyleSheet(self._linear_gradient(self._current_alpha))
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
        self.bg_image_label.setPixmap(QPixmap())

        if not image_path or not os.path.exists(image_path):
            self._has_image = False
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
            return

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            label_size = self.bg_image_label.size()
            if label_size.width() > 0 and label_size.height() > 0:
                scaled_pixmap = pixmap.scaled(
                    label_size,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                self.bg_image_label.setPixmap(scaled_pixmap)
            else:
                self.bg_image_label.setPixmap(pixmap)

            self._has_image = True
            self.bg_image_label.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                    padding: 0px;
                }
            """)
            self.name_label.setStyleSheet(self._linear_gradient(self._current_alpha))
        else:
            self._has_image = False
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


class ConnectPage(AbstractPage):
    def __init__(self, config: ConfigData, flight: FlightData, module_data: ModuleData, parent=None):
        super().__init__(config, flight, parent)
        self.module_data = module_data
        self.platforms = {
            FlightSim.DCS: {'name': FlightSim.DCS.full_name, 'image_path': 'assets/DCS.jpg'},
            FlightSim.FS2020: {'name': FlightSim.FS2020.full_name, 'image_path': 'assets/FS2020.jpg'},
        }
        self.aircrafts = []
        self._current_model = flight['Connect']['model']
        self._current_platform = self.get_platform(self._current_model) if self._current_model else None

        self.connectLayout = self.page_layout
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
        self.flightSimSelect.currentIndexChanged.connect(self.on_platform_changed)
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

        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.gallery_container = QWidget()
        self.gallery_layout = QVBoxLayout(self.gallery_container)
        self.gallery_layout.setSpacing(8)
        self.gallery_layout.setContentsMargins(0, 0, 4, 0)
        self.gallery_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(self.gallery_container)

        self.panel_container = QWidget()
        self.panel_layout = QVBoxLayout(self.panel_container)
        self.panel_layout.setContentsMargins(0, 0, 4, 0)
        self.panel_layout.setAlignment(Qt.AlignTop)
        self.panel_layout.setSpacing(8)

        image_section = QWidget()
        image_layout = QVBoxLayout(image_section)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        self.image_label = ImageLabel(radius=8)
        self.image_label.setMinimumHeight(80)
        self.image_label.setMaximumHeight(120)
        image_layout.addWidget(self.image_label)

        self.module_name_label = QLabel()
        self.module_name_label.setParent(self.image_label)
        self.module_name_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                background: transparent;
                padding: 4px 4px;
            }
        """)

        self.status_label = QLabel()
        self.status_label.setParent(self.image_label)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-weight: 500;
                color: #d4d4d4;
                background: transparent;
                padding: 24px 6px;
            }
        """)

        data_panel = QWidget()
        data_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        data_layout = QVBoxLayout(data_panel)
        data_layout.setAlignment(Qt.AlignCenter)

        self.panel_layout.addWidget(image_section)
        self.panel_layout.addWidget(data_panel, 1)

        self.panel_container.hide()
        self.main_layout.addWidget(self.panel_container)

        self.scroll_area.setWidget(self.main_container)

        self.connectLayout.addWidget(self.scroll_area)

        self._module_items = {}

        self._initialize_aircrafts()
        self._initialize_ui()

    def _initialize_aircrafts(self):
        for mod_id, data in self.module_data.items():
            dir, module = data
            if 'Manifest' in module:
                mod_id = module['Manifest']['model']
                sim = module['Manifest']['platform']
                name = module['Manifest']['title']
                self.aircrafts.append(
                    {
                        'key': mod_id,
                        'name': name,
                        'image_path': os.path.join(dir, 'bg_image.jpg'),
                        'platform': FlightSim(sim),
                    }
                )

    def _initialize_ui(self):
        platforms = [(simid, detail['name']) for simid, detail in self.platforms.items()]
        self._populate_platforms(platforms)

        if self._current_model and self._current_platform:
            index = self.flightSimSelect.findData(self._current_platform)
            if index >= 0:
                self.flightSimSelect.setCurrentIndex(index)
            self.gallery_container.hide()
            self.panel_container.show()
            self.update_panel_info(self._current_platform, self._current_model)
        elif platforms:
            self.flightSimSelect.setCurrentIndex(0)
            self._load_modules_for_platform(platforms[0][0])
            self.gallery_container.show()
            self.panel_container.hide()

    def _populate_platforms(self, platforms):
        self.flightSimSelect.clear()
        for simid, name in platforms:
            self.flightSimSelect.addItem(name, simid)

    def _load_modules_for_platform(self, platform):
        for module in self.aircrafts:
            key = module['key']
            if key not in self._module_items:
                card = ImageCard(key, module['name'])
                card.clicked.connect(lambda key=key: self.on_module_clicked(key))
                self._module_items[key] = card
                self.gallery_layout.addWidget(card)

                image_path = module['image_path']
                card._image_path = image_path
                card.set_background_image(image_path)

        for key, card in self._module_items.items():
            module = next((m for m in self.aircrafts if m['key'] == key), None)
            if module:
                card.setVisible(module['platform'] == platform)

        self._current_platform = platform

    def update_ui(self):
        self.flightSimSelect.blockSignals(True)
        model = self.flight['Connect']['model']
        platform = self.module_data[model][1]['Manifest']['platform'] if model in self.module_data else None
        if platform:
            index = self.flightSimSelect.findData(FlightSim(platform))
            if index >= 0:
                self.flightSimSelect.setCurrentIndex(index)
        self.flightSimSelect.blockSignals(False)

        selected_platform = self.flightSimSelect.currentData()
        if selected_platform and selected_platform != self._current_platform:
            self._load_modules_for_platform(selected_platform)

        if model and selected_platform:
            self.gallery_container.hide()
            self.panel_container.show()
            self.update_panel_info(selected_platform, model)
        else:
            self.gallery_container.show()
            self.panel_container.hide()

    def update_panel_info(self, platform, module_id):
        module = self.get_module(module_id, platform)

        if module:
            module_name = module.get('name', module_id)
            self.module_name_label.setText(module_name)
            self.module_name_label.adjustSize()
            self.status_label.setText(f'NO CONNECTION TO {self.platforms[platform]["name"].upper()}')
            self.status_label.adjustSize()

            image_path = module.get('image_path')
            if not image_path or not os.path.exists(image_path):
                image_path = self.platforms[platform]['image_path']

            pixmap = QPixmap(image_path)
            if image_path and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setScaledContents(True)
            else:
                self.image_label.setPixmap(None)
                self.image_label.setStyleSheet("""
                    ImageLabel {
                        background-color: #f8f9fa;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                    }
                """)

    def on_platform_changed(self):
        platform = self.flightSimSelect.currentData()
        if platform is not None:
            self._load_modules_for_platform(platform)
            self.gallery_container.show()
            self.panel_container.hide()

    def on_module_clicked(self, module_id):
        platform = self.flightSimSelect.currentData()
        if platform is not None:
            self.handle_module_clicked(platform, module_id)
            self.state_changed.emit()
            self.update_ui()

    def handle_module_clicked(self, platform: str, module_id: str):
        module = self.get_module(module_id, platform)

        if not module:
            return

        self.flight['Connect']['model'] = module_id
        module_data = self.module_data[module_id][1]
        self.flight['Input'] = module_data['Data']

    def get_platform(self, module_id):
        module = self.get_module(module_id)
        return module['platform'] if module else None

    def modules_from(self, platform):
        return [m for m in self.aircrafts if m['platform'] == platform]

    def get_module(self, module_id, platform=None):
        if platform:
            for module in self.modules_from(platform):
                if module['key'] == module_id:
                    return module
        else:
            for module in self.aircrafts:
                if module['key'] == module_id:
                    return module
        return {}