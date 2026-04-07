import os

from PySide2.QtCore import QSize, Qt, QTimer, Signal
from PySide2.QtGui import QDoubleValidator, QIntValidator, QPainter, QPainterPath, QPixmap, QColor
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import i18n
from data.config import ConfigData
from data.flight import FlightData
from flightsim.dcs.connect import DCSConnect
from flightsim.module import FlightSim, ModuleData, controller_manager
from lib.screen import ScreenGeometry
from type.widget import OptionWidget

from . import AbstractPage


class ImagePixmap(QLabel):
    def __init__(self, parent=None, radius=4, opacity=1):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = QPixmap()
        self.radius = radius
        self.opacity = opacity

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

        overlay_path = QPainterPath()
        overlay_path.addRoundedRect(rect, self.radius, self.radius)
        painter.fillPath(overlay_path, QColor(0, 0, 0, 255 * (1 - self.opacity)))


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

        self.bg_image_label = ImagePixmap(self.image_container, radius=8, opacity=0.9)
        self.bg_image_label.setObjectName('bgImageLabel')
        self.bg_image_label.setMinimumHeight(130)
        container_layout.addWidget(self.bg_image_label)

        self.name_label = QLabel(module_name, self.image_container)
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

    def _linear_gradient(self, alpha):
        return f"""
            ImageCard #nameLabel {{
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
            self._start_transition(150)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._has_image:
            self._start_transition(100)
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
                ImageCard #bgImageLabel {
                    background-color: #dcdcdc;
                    border-radius: 8px;
                    padding: 0px;
                }
            """)
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
            return

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(QSize(200, 260), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.bg_image_label.setPixmap(scaled_pixmap)

            self._has_image = True
            self.bg_image_label.setStyleSheet("""
                ImageCard #bgImageLabel {
                    border-radius: 8px;
                    padding: 0px;
                }
            """)
            self.name_label.setStyleSheet(self._linear_gradient(self._current_alpha))
        else:
            self._has_image = False
            self.bg_image_label.setStyleSheet("""
                ImageCard #bgImageLabel {
                    background-color: #dcdcdc;
                    border-radius: 8px;
                    padding: 0px;
                }
            """)
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
    def __init__(
        self, win: ScreenGeometry, config: ConfigData, flight: FlightData, module_data: ModuleData, parent=None
    ):
        super().__init__(win, config, flight, parent)
        self.flightsims = {
            FlightSim.DCS: {'name': FlightSim.DCS.full_name, 'image_path': 'assets/DCS.jpg'},
            FlightSim.FS2020: {'name': FlightSim.FS2020.full_name, 'image_path': 'assets/FS2020.jpg'},
        }
        self.modules = {}
        self.connector = DCSConnect(self.flight)

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
        self.flightSimSelect = QComboBox()
        size_policy = self.flightSimSelect.sizePolicy()
        size_policy.setVerticalPolicy(size_policy.Fixed)
        self.flightSimSelect.setSizePolicy(size_policy)
        self.flightSimSelect.setMinimumWidth(120)
        self.flightSimSelect.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 10px;
                background: white;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #4a90e2;
            }
            QComboBox:focus {
                border-color: #4a90e2;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 18px;
                height: 18px;
                image: url(assets/down_arrow.svg);
            }
        """
        )
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
        image_layout = QVBoxLayout(image_section)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        self.image_label = ImagePixmap(radius=8, opacity=0.7)
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

        return_label = QLabel()
        return_label.setText(i18n.t('BackToModules'))
        return_label.setObjectName('returnLabel')
        return_label.setAlignment(Qt.AlignCenter)
        return_label.setStyleSheet("""
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
        size_policy = return_label.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Minimum)
        return_label.setSizePolicy(size_policy)
        return_label.adjustSize()
        return_label.setCursor(Qt.PointingHandCursor)
        return_label.mousePressEvent = self.on_return_clicked

        self.panel_layout.addWidget(image_section)
        self.panel_layout.addWidget(flight_panel, 1)
        self.panel_layout.addWidget(return_label, 0, Qt.AlignCenter)

        self.panel_container.hide()

        self.scroll_area.setWidget(self.list_container)

        self.connectLayout.addWidget(self.scroll_area)
        self.connectLayout.addWidget(self.panel_container)

        self._module_list = {}

        self.init_modules(module_data)
        self.init_ui()
        self.retranslate_ui()

    def init_modules(self, module_data: ModuleData):
        for mod_id, data in module_data.items():
            dir, manifest = data
            if 'Module' in manifest:
                mod_id = manifest['Module']['model']
                sim_id = manifest['Module']['platform']
                name = manifest['Module']['title']
                module = {
                    'key': mod_id,
                    'name': name,
                    'image_path': os.path.join(dir, 'bg_image.jpg'),
                    'control': manifest['Data']['flight_mode'],
                    'platform': FlightSim(sim_id),
                    'data': manifest['Data'],
                }
                self.modules[mod_id] = module

        self._current_model = self.flight['Connect']['model']
        self._current_platform = self.get_platform(self._current_model) if self._current_model else None

    def init_ui(self):
        platforms = [(simid, detail['name']) for simid, detail in self.flightsims.items()]
        self._populate_selections(platforms)

        if self._current_model and self._current_platform:
            index = self.flightSimSelect.findData(self._current_platform)
            if index >= 0:
                self.flightSimSelect.setCurrentIndex(index)
            self.scroll_area.hide()
            self.panel_container.show()
            self._populate_modules(self._current_platform)
            self.update_panel(self._current_platform, self._current_model)
        elif platforms:
            self.flightSimSelect.setCurrentIndex(0)
            self._populate_modules(platforms[0][0])
            self.scroll_area.show()
            self.panel_container.hide()

    def _populate_selections(self, platforms):
        self.flightSimSelect.blockSignals(True)
        self.flightSimSelect.clear()
        for simid, name in platforms:
            self.flightSimSelect.addItem(name, simid)
        self.flightSimSelect.blockSignals(False)

    def _populate_modules(self, platform):
        for module in self.modules.values():
            key = module['key']
            if key not in self._module_list:
                card = ImageCard(key, module['name'])
                card.clicked.connect(lambda key=key: self.on_module_clicked(key))
                self._module_list[key] = card
                self.list_layout.addWidget(card)

                image_path = module['image_path']
                card._image_path = image_path
                card.set_background_image(image_path)

        for key, card in self._module_list.items():
            module = self.modules.get(key)
            if module:
                card.setVisible(module['platform'] == platform)

        self._current_platform = platform

    def _render_controllers(self, name):
        self._clear_controllers()

        metadata = controller_manager.get_metadata(name)
        if not metadata or 'options' not in metadata:
            return

        for option, widget, default in metadata['options']:
            h_layout = QHBoxLayout()
            h_layout.setSpacing(10)
            h_layout.setContentsMargins(0, 0, 0, 0)

            text = metadata.get('i18n', {}).get(option, {})
            name = f'{option}Label'
            label = QLabel()
            label.setText(i18n.t(text))
            label.setObjectName(name)
            label.setMinimumWidth(120)
            h_layout.addWidget(label)

            spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            h_layout.addItem(spacer)

            if widget == OptionWidget.CheckBox:
                checkbox = QCheckBox()
                checkbox.setObjectName(f'{option}Option')
                if self.flight.has(option):
                    value = self.flight.get(option)
                    if isinstance(value, str):
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        else:
                            value = False
                    checkbox.setChecked(bool(value))
                else:
                    self.flight.set(option, default)
                    checkbox.setChecked(default)

                checkbox.stateChanged.connect(lambda state, opt=option: self.flight.set(opt, bool(state)))
                h_layout.addWidget(checkbox)

                self._controller_widgets[option] = {
                    'label': label,
                    'checkbox': checkbox,
                    'layout': h_layout,
                }

            elif widget == OptionWidget.LineEdit:
                line_edit = QLineEdit()
                line_edit.setObjectName(f'{option}Option')
                line_edit.setStyleSheet(
                    """
                    QLineEdit {
                        border: 1px solid #e0e0e0;
                        border-radius: 6px;
                        padding: 6px 10px;
                        background: white;
                        min-width: %dpx;
                        max-width: %dpx;
                        font-size: 13px;
                    }
                    QLineEdit:hover {
                        border-color: #4a90e2;
                    }
                    QLineEdit:focus {
                        border-color: #4a90e2;
                        outline: none;
                    }
                """
                    % (100, 100)
                )

                if self.flight.has(option):
                    value = self.flight.get(option)
                else:
                    value = default
                    self.flight.set(option, value)

                if isinstance(value, int):
                    line_edit.setValidator(QIntValidator())
                elif isinstance(value, float):
                    line_edit.setValidator(QDoubleValidator())

                line_edit.setText(str(value))

                line_edit.textChanged.connect(lambda text, opt=option: self.flight.set(opt, str(text)))

                h_layout.addWidget(line_edit)

                self._controller_widgets[option] = {
                    'label': label,
                    'line_edit': line_edit,
                    'layout': h_layout,
                }

            elif widget == OptionWidget.SpinBox:
                spin_box = QSpinBox()
                spin_box.setObjectName(f'{option}Option')
                spin_box.setStyleSheet(
                    """
                    QSpinBox {
                        border: 1px solid #e0e0e0;
                        border-radius: 6px;
                        padding: 6px 10px;
                        background: white;
                        min-width: %dpx;
                        max-width: %dpx;
                        font-size: 13px;
                    }
                    QSpinBox:hover {
                        border-color: #4a90e2;
                    }
                    QSpinBox:focus {
                        border-color: #4a90e2;
                        outline: none;
                    }
                    QSpinBox::up-button, QSpinBox::down-button {
                        background: transparent;
                        border: none;
                        width: 16px;
                    }
                """
                    % (100, 100)
                )
                spin_box.setMinimum(0)
                spin_box.setMaximum(1000000)

                if self.flight.has(option):
                    value = self.flight.get(option)
                    try:
                        value = int(value)
                    except ValueError:
                        value = default
                else:
                    value = default
                    self.flight.set(option, value)

                spin_box.setValue(value)

                spin_box.valueChanged.connect(lambda value, opt=option: self.flight.set(opt, value))

                h_layout.addWidget(spin_box)

                self._controller_widgets[option] = {
                    'label': label,
                    'spin_box': spin_box,
                    'layout': h_layout,
                }

            self.flight_layout.addLayout(h_layout)

        self.flight_layout.addStretch(1)

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
        model = self._current_model
        platform = self._current_platform

        self.flightSimSelect.blockSignals(True)
        if platform:
            index = self.flightSimSelect.findData(FlightSim(platform))
            if index >= 0:
                self.flightSimSelect.setCurrentIndex(index)
        self.flightSimSelect.blockSignals(False)

        if model and platform:
            self.scroll_area.hide()
            self.panel_container.show()
            self.update_panel(platform, model)
        else:
            self.scroll_area.show()
            self.panel_container.hide()

    def on_return_clicked(self, _):
        self.scroll_area.show()
        self.panel_container.hide()

    def update_panel(self, sim_id, module_id):
        module = self.get_module(module_id)

        if module:
            module_name = module.get('name', module_id)
            self.module_name_label.setText(module_name)
            self.module_name_label.adjustSize()
            self.status_label.setText(f'NO CONNECTION TO {self.flightsims[sim_id]["name"].upper()}')
            self.status_label.adjustSize()

            image_path = module.get('image_path')
            if not image_path or not os.path.exists(image_path):
                image_path = self.flightsims[sim_id]['image_path']

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

            flight_mode = module.get('control', 0)
            self._render_controllers(flight_mode)

    def on_platform_changed(self):
        platform = self.flightSimSelect.currentData()
        if platform is not None:
            self._populate_modules(platform)
            self.scroll_area.show()
            self.panel_container.hide()

    def on_module_clicked(self, module_id):
        module = self.get_module(module_id)
        if not module:
            return

        self.flight['Connect']['model'] = module_id
        self.flight['Input'] = {
            k: module['data'][k] if k in module['data'] else v for k, v in self.flight['Input'].items()
        }

        self._current_model = module_id
        self._current_platform = module['platform']

        self.state_changed.emit()
        self.update_ui()

    def get_module(self, module_id):
        return self.modules.get(module_id)

    def get_platform(self, module_id) -> FlightSim:
        module = self.get_module(module_id)
        return module['platform'] if module else None

    def retranslate_ui(self):
        """Update UI translations."""
        self.flightSimLabel.setText(i18n.t('FlightSim'))

        if self._controller_widgets:
            if self._current_model:
                module = self.get_module(self._current_model)
                if module:
                    flight_mode = module.get('control', 0)
                    metadata = controller_manager.get_metadata(flight_mode)
                    if metadata and 'options' in metadata:
                        for option, widget, default in metadata['options']:
                            if option in self._controller_widgets and 'label' in self._controller_widgets[option]:
                                text = metadata.get('i18n', {}).get(option, {})
                                self._controller_widgets[option]['label'].setText(i18n.t(text))

        for widget in self.panel_container.findChildren(QLabel):
            if widget.objectName() == 'returnLabel':
                widget.setText(i18n.t('BackToModules'))