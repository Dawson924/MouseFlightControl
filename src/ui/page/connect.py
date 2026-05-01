import os
from typing import Any

from PySide2.QtCore import QSize, Qt, QTimer, Signal
from PySide2.QtGui import QColor, QDoubleValidator, QIntValidator, QLinearGradient, QPainter, QPainterPath, QPixmap
from PySide2.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

import i18n
from connect.flight import FlightConnect
from connect.module import FlightSim, ModuleRegistry, controllers
from data.config import Config
from data.flight import FlightInput
from lib.container import store
from lib.screen import ScreenGeometry
from type.widget import OptionWidget
from ui.widgets import ComboBox, LineEdit, SpinBox
from ui.factory import WidgetFactory

from . import AbstractPage


class ImagePixmap(QLabel):
    def __init__(self, parent=None, radius=4, opacity=1, gradient=0):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = QPixmap()
        self.radius = radius
        self.opacity = opacity
        self.alpha = gradient

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()

    def setGradientAlpha(self, alpha):
        self.alpha = alpha
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

        # Background overlay
        overlay_path = QPainterPath()
        overlay_path.addRoundedRect(rect, self.radius, self.radius)
        painter.fillPath(overlay_path, QColor(0, 0, 0, 255 * (1 - self.opacity)))

        # Background gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(1, QColor(0, 0, 0, self.alpha))
        painter.fillPath(overlay_path, gradient)


class ImageCard(QFrame):
    clicked = Signal(str)

    def __init__(self, id, text, parent=None):
        super().__init__(parent)
        self.id = id
        self.text = text

        self.setStyleSheet("""
            ImageCard {
                background-color: #f8f9fa;
            }
            ImageCard:hover {
                background-color: #eef2f7;
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

        self.bg_image_label = ImagePixmap(self.image_container, radius=8, opacity=1, gradient=100)
        self.bg_image_label.setObjectName('bgImageLabel')
        self.bg_image_label.setMinimumHeight(130)
        container_layout.addWidget(self.bg_image_label)

        self.name_label = QLabel(text, self.image_container)
        self.name_label.setObjectName('nameLabel')
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        layout.addWidget(self.image_container)

        self.setCursor(Qt.PointingHandCursor)

        self._has_image = False
        self._current_alpha = 100
        self._target_alpha = 150
        self._transition_timer = QTimer(self)
        self._transition_timer.setInterval(16)
        self._transition_timer.timeout.connect(self._on_transition_tick)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.image_container.width()
        h = self.name_label.sizeHint().height()
        container_h = self.image_container.height()
        self.name_label.setGeometry(0, container_h - h, w, h)

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
        self.bg_image_label.setGradientAlpha(self._current_alpha)
        if self._current_alpha == self._target_alpha:
            self._transition_timer.stop()

    def enterEvent(self, event):
        if self._has_image:
            self._start_transition(150)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._has_image:
            self._start_transition(100)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.id)
        super().mousePressEvent(event)

    def set_background_image(self, image_path):
        self.bg_image_label.setPixmap(QPixmap())

        # if not image_path or not os.path.exists(image_path):
        #     self._has_image = False
        #     self.bg_image_label.setStyleSheet("""
        #         ImageCard #bgImageLabel {
        #             background-color: #dcdcdc;
        #             border-radius: 8px;
        #             padding: 0px;
        #         }
        #     """)
        #     self.name_label.setStyleSheet("""
        #         ImageCard #nameLabel {
        #             font-size: 14px;
        #             font-weight: 500;
        #             color: #2c3e50;
        #             background-color: transparent;
        #             margin-left: 4px;
        #             padding-bottom: 6px;
        #         }
        #     """)
        #     return

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(QSize(200, 260), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.bg_image_label.setPixmap(scaled_pixmap)

            self._has_image = True
            self.name_label.setStyleSheet("""
                ImageCard #nameLabel {
                    font-size: 14px;
                    font-weight: 500;
                    color: #d0d0d0;
                    background-color: transparent;
                    padding: 18px 8px 6px 8px;
                }
            """)
        else:
            self._has_image = False
            self.name_label.setStyleSheet("""
                ImageCard #nameLabel {
                    font-size: 14px;
                    font-weight: 500;
                    color: #2c3e50;
                    background-color: transparent;
                    margin-left: 4px;
                    padding-bottom: 6px;
                }
            """)


class ConnectPage(AbstractPage):
    def __init__(self, win: ScreenGeometry, config: Config, flight: FlightInput, modules: ModuleRegistry, parent=None):
        super().__init__(win, config, flight, parent)
        self.flightsims = {
            FlightSim.DCS: {'name': FlightSim.DCS.full_name, 'image_path': 'assets/Default.jpg'},
            FlightSim.FS2020: {'name': FlightSim.FS2020.full_name, 'image_path': 'assets/Default.jpg'},
        }
        self.modules = {}
        self._controller_widgets = {}
        self.connector: FlightConnect = store.get('connector')

        self._image_cache = {}
        self._last_image_path = None

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_connection)
        self.status_timer.start(1000)

        self.connectLayout = self.page_layout
        self.connectLayout.setSpacing(10)
        self.connectLayout.setContentsMargins(0, 0, 0, 0)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        self.flightSimLabel = QLabel()
        self.flightSimLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
            }
        """)
        h_layout.addWidget(self.flightSimLabel)
        self.flightSimSelect = ComboBox()
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

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setAlignment(Qt.AlignTop)

        self.panel_container = QWidget()
        self.panel_layout = QVBoxLayout(self.panel_container)
        self.panel_layout.setContentsMargins(0, 0, 4, 0)
        self.panel_layout.setAlignment(Qt.AlignTop)
        self.panel_layout.setSpacing(8)

        image_section = QWidget()
        image_layout = QGridLayout(image_section)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        self.image_label = ImagePixmap(radius=8, opacity=0.7)
        self.image_label.setMinimumHeight(80)
        self.image_label.setMaximumHeight(120)
        image_layout.addWidget(self.image_label, 0, 0)

        self.title_container = QWidget()
        self.title_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        self.title_container.setFixedHeight(50)
        self.title_layout = QVBoxLayout(self.title_container)
        self.title_layout.setContentsMargins(8, 6, 6, 6)
        self.title_layout.setSpacing(0)

        self.sim_label = QLabel()
        self.sim_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                background: transparent;
            }
        """)
        self.title_layout.addWidget(self.sim_label)

        self.module_label = QLabel()
        self.module_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-weight: 500;
                color: #d4d4d4;
                background: transparent;
            }
        """)
        self.title_layout.addWidget(self.module_label)

        image_layout.addWidget(self.title_container, 0, 0, Qt.AlignTop | Qt.AlignLeft)

        flight_panel = QWidget()
        flight_panel.setObjectName('flightPanel')
        flight_panel.setStyleSheet("""
            #flightPanel {
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        self.flight_layout = QVBoxLayout(flight_panel)
        self.flight_layout.setContentsMargins(10, 10, 10, 10)

        self.returnLabel = QLabel()
        self.returnLabel.setText(i18n.t('BackToModules'))
        self.returnLabel.setObjectName('returnLabel')
        self.returnLabel.setAlignment(Qt.AlignCenter)
        self.returnLabel.setStyleSheet("""
            #returnLabel {
                font-size: 11px;
                font-weight: 400;
                color: dimgray;
                background-color: transparent;
                border-radius: 4px;
                padding: 6px 8px;
            }
            #returnLabel:hover {
                background-color: #e0e0e0;
            }
        """)
        size_policy = self.returnLabel.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Minimum)
        self.returnLabel.setSizePolicy(size_policy)
        self.returnLabel.adjustSize()
        self.returnLabel.setCursor(Qt.PointingHandCursor)
        self.returnLabel.mousePressEvent = self.on_return_clicked

        self.panel_layout.addWidget(image_section)
        self.panel_layout.addWidget(flight_panel, 1)
        self.panel_layout.addWidget(self.returnLabel, 0, Qt.AlignCenter)

        self.panel_container.hide()

        self.scroll_area.setWidget(self.list_container)

        self.connectLayout.addWidget(self.scroll_area)
        self.connectLayout.addWidget(self.panel_container)

        self._module_list = {}

        self.init_modules(modules)
        self.init_ui()
        self.retranslate_ui()

    def init_modules(self, module_data: ModuleRegistry):
        self.modules = module_data
        self._model = self.flight['Connect']['model']
        self._platform = self.get_platform(self._model)

    def init_ui(self):
        platforms = [(simid, detail['name']) for simid, detail in self.flightsims.items()]
        self._populate_platforms(platforms)

        if self._model and self._platform:
            index = self.flightSimSelect.findData(self._platform)
            if index >= 0:
                self.flightSimSelect.setCurrentIndex(index)
            self.scroll_area.hide()
            self.panel_container.show()
            self._populate_modules(self._platform)
            self.update_ui()
        elif platforms:
            self.flightSimSelect.setCurrentIndex(0)
            self._populate_modules(platforms[0][0])
            self.scroll_area.show()
            self.panel_container.hide()

    def _populate_platforms(self, platforms):
        self.flightSimSelect.blockSignals(True)
        self.flightSimSelect.clear()
        for simid, name in platforms:
            self.flightSimSelect.addItem(name, simid)
        self.flightSimSelect.blockSignals(False)

    def _populate_modules(self, platform):
        grouped_modules = {}

        for mod_id, module in self.modules.items():
            if module['platform'] != platform:
                continue

            image_path = module['image_path']
            name = module['name']
            key = (image_path, name)

            if key not in grouped_modules:
                grouped_modules[key] = {'ids': [], 'module': module}
            grouped_modules[key]['ids'].append(mod_id)

        for (image_path, name), data in grouped_modules.items():
            ids = data['ids']
            module = data['module']

            display_name = f'{name} ({len(ids)})' if len(ids) > 1 else name
            primary_id = ids[0]

            if primary_id not in self._module_list:
                card = ImageCard(primary_id, display_name)
                card.clicked.connect(lambda key=primary_id: self.on_module_clicked(key))
                self._module_list[primary_id] = card
                self.list_layout.addWidget(card)
                card._image_path = image_path
                card.set_background_image(image_path)
                card._model_ids = ids
            else:
                card = self._module_list[primary_id]
                card.text = display_name
                card._model_ids = ids
                card.name_label.setText(display_name)

        for card_id, card in self._module_list.items():
            module = self.modules.get(card_id)
            card.setVisible(module is not None and module['platform'] == platform)

        self._platform = platform

    def _set_module_label(self, text, active=False):
        if active:
            self.module_label.setText(text)
            self.module_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 500;
                    color: #d4d4d4;
                    background: transparent;
                }
            """)
        else:
            self.module_label.setText(text)
            self.module_label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    font-weight: 500;
                    color: #d4d4d4;
                    background: transparent;
                }
            """)

    def _set_image_label(self, image_path):
        if image_path == self._last_image_path:
            return

        self._last_image_path = image_path

        if not image_path:
            self.image_label.setPixmap(None)
            self.image_label.setStyleSheet("""
                ImageLabel {
                    background-color: #f8f9fa;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                }
            """)
            return

        cache_key = image_path

        if cache_key in self._image_cache:
            scaled_pixmap = self._image_cache[cache_key]
        else:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.image_label.setPixmap(None)
                self.image_label.setStyleSheet("""
                    ImageLabel {
                        background-color: #f8f9fa;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                    }
                """)
                return

            width = self.image_label.width()
            height = self.image_label.height()
            scaled_pixmap = pixmap.scaled(
                width,
                height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            self._image_cache[cache_key] = scaled_pixmap

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setScaledContents(True)

    def _render_controllers(self, name):
        self._clear_controllers()

        metadata = controllers.get_metadata(name)
        if not metadata or 'options' not in metadata:
            return

        spec_group = {}
        for option, widget, default in metadata['options']:
            widget_type = ''
            if widget == OptionWidget.CheckBox:
                widget_type = 'CheckBox'
            elif widget == OptionWidget.LineEdit:
                widget_type = 'LineEdit'
            elif widget == OptionWidget.SpinBox:
                widget_type = 'SpinBox'

            if self.flight.has(option):
                value = self.flight.get(option)
            else:
                value = default
                self.flight.set(option, value)

            spec_group[option] = {
                'widget': widget_type,
                'i18n': metadata.get('i18n', {}).get(option, ''),
                'default': default,
                'value': value
            }

        self._controller_widgets = WidgetFactory.populate_from_spec(
            self.flight_layout,
            spec_group,
            self.set_flight_option,
            self
        )

        for option, spec in spec_group.items():
            widget = self._controller_widgets.get(option)
            if widget:
                if spec['widget'] == 'CheckBox':
                    if isinstance(spec['value'], str):
                        if spec['value'].lower() == 'true':
                            spec['value'] = True
                        elif spec['value'].lower() == 'false':
                            spec['value'] = False
                        else:
                            spec['value'] = False
                    widget.setChecked(bool(spec['value']))
                elif spec['widget'] == 'LineEdit':
                    widget.setText(str(spec['value']))
                    if isinstance(spec['value'], int):
                        widget.setValidator(QIntValidator())
                    elif isinstance(spec['value'], float):
                        widget.setValidator(QDoubleValidator())
                elif spec['widget'] == 'SpinBox':
                    try:
                        widget.setValue(int(spec['value']))
                    except ValueError:
                        widget.setValue(spec['default'])

        WidgetFactory.add_stretch(self.flight_layout)

    def set_flight_option(self, key: str, value: Any):
        self.flight.set(key, value)

    def _clear_controllers(self):
        while self.flight_layout.count():
            item = self.flight_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

        self._controller_widgets = {}

    def _delete_layout(self, layout):
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

        layout.deleteLater()

    def update_ui(self):
        model = self._model
        platform = self._platform

        self.flightSimSelect.blockSignals(True)
        if platform:
            index = self.flightSimSelect.findData(FlightSim(platform))
            if index >= 0:
                self.flightSimSelect.setCurrentIndex(index)
        self.flightSimSelect.blockSignals(False)

        if model and platform:
            self.scroll_area.hide()
            self.panel_container.show()
            self.sim_label.setText(self.flightsims[platform]['name'])
            module = self.get_module(model)
            if module:
                self._render_controllers(module.get('control', 0))
        else:
            self.scroll_area.show()
            self.panel_container.hide()

    def on_return_clicked(self, _):
        self.scroll_area.show()
        self.panel_container.hide()

    def check_connection(self):
        data = self.connector.get_data()
        if not data:
            self._set_module_label('NO CONNECTION', False)
            if self._platform:
                image_path = self.flightsims[self._platform]['image_path']
                self._set_image_label(image_path)
            return

        elif data.model == 'Spectator':
            #     self._set_module_label('CONNECTED', False)
            #     if self._platform:
            #         image_path = self.flightsims[self._platform]['image_path']
            #         self._set_image_label(image_path)
            #     return
            return

        elif data.model != self._model and self.config['auto_connect']:
            print(data.model)
            self.change_module(data.model)
            self.update_ui()

            module = self.get_module(self._model)
            if module:
                name = module.get('name', self._model)
                self._set_module_label(name, True)
                image_path = module.get('image_path')
                if not image_path or not os.path.exists(image_path):
                    image_path = self.flightsims[self._platform]['image_path']
                self._set_image_label(image_path)

    def on_platform_changed(self):
        platform = self.flightSimSelect.currentData()
        if platform is not None:
            self._populate_modules(platform)
            self.scroll_area.show()
            self.panel_container.hide()

    def on_module_clicked(self, module_id):
        self.config['auto_connect'] = False
        self.change_module(module_id)
        self.update_ui()

    def change_module(self, module_id):
        module = self.get_module(module_id)
        if not module:
            return

        self.flight['Connect']['model'] = module_id
        self.flight['Input'] = {
            k: module['data'][k] if k in module['data'] else v for k, v in self.flight['Input'].items()
        }

        self._model = module_id
        self._platform = module['platform']

    def get_module(self, module_id):
        return self.modules.get(module_id)

    def get_platform(self, module_id) -> FlightSim:
        module = self.get_module(module_id)
        return module['platform'] if module else None

    def retranslate_ui(self):
        self.flightSimLabel.setText(i18n.t('FlightSim'))
        self.returnLabel.setText(i18n.t('BackToModules'))

        if self._controller_widgets and self._model:
            module = self.get_module(self._model)
            if module:
                flight_mode = module.get('control', 0)
                metadata = controllers.get_metadata(flight_mode)
                if metadata and 'options' in metadata:
                    spec_group = {}
                    for option, widget, default in metadata['options']:
                        spec_group[option] = {
                            'i18n': metadata.get('i18n', {}).get(option, '')
                        }
                    WidgetFactory.retranslate_from_spec(spec_group, self)