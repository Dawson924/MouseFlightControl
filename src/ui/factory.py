from typing import Any, Callable, Dict, Tuple

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QWidget,
)

import i18n
from ui.widgets import KeybindEdit, LineEdit, SpinBox


class WidgetFactory:
    @staticmethod
    def create_widget(
        field_name: str,
        spec: Dict[str, Any],
        on_change: Callable[[Any], None],
        parent: QWidget = None,
        custom_widget=None,
    ) -> Tuple[QWidget, QLabel]:
        widget_type = spec.get('widget')
        widget = custom_widget
        label = QLabel(parent)

        if widget is None:
            if widget_type == 'CheckBox':
                widget = QCheckBox(parent)
                widget.stateChanged.connect(lambda state, fn=on_change: fn(bool(state)))

            elif widget_type == 'SpinBox':
                widget = SpinBox(parent)
                if 'min' in spec:
                    widget.setMinimum(spec['min'])
                if 'max' in spec:
                    widget.setMaximum(spec['max'])
                widget.valueChanged.connect(on_change)

            elif widget_type == 'Slider':
                widget = QSlider(Qt.Horizontal, parent)
                if 'min' in spec:
                    widget.setMinimum(spec['min'])
                if 'max' in spec:
                    widget.setMaximum(spec['max'])
                widget.setTickPosition(QSlider.TicksBelow)
                widget.setTickInterval(1)
                widget.valueChanged.connect(on_change)

            elif widget_type == 'KeybindEdit':
                widget = KeybindEdit(parent)
                widget.textChanged.connect(on_change)

            elif widget_type == 'LineEdit':
                widget = LineEdit(parent)
                widget.textChanged.connect(on_change)

        label.setObjectName(f'{field_name}Label')

        return widget, label

    @staticmethod
    def create_row(
        field_name: str,
        spec: Dict[str, Any],
        on_change: Callable[[Any], None],
        parent: QWidget = None,
        custom_widget=None,
    ) -> Tuple[QHBoxLayout, QWidget, QLabel]:
        widget, label = WidgetFactory.create_widget(field_name, spec, on_change, parent, custom_widget)

        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(label)
        layout.addStretch()

        if widget:
            layout.addWidget(widget)

        return layout, widget, label

    @staticmethod
    def populate_from_spec(
        container_layout,
        spec_group: Dict[str, Dict[str, Any]],
        on_change: Callable[[str, Any], None],
        parent: QWidget = None,
        custom_widgets: Dict[str, QWidget] = None,
        custom_callbacks: Dict[str, Callable[[Any], None]] = None,
    ) -> Dict[str, QWidget]:
        widgets = {}
        custom_widgets = custom_widgets or {}
        custom_callbacks = custom_callbacks or {}

        for field_name, field_spec in spec_group.items():
            if 'widget' not in field_spec:
                continue

            callback = custom_callbacks.get(field_name) or (
                lambda value, fn=on_change, fn_field=field_name: fn(fn_field, value)
            )
            custom_widget = custom_widgets.get(field_name)

            layout, widget, label = WidgetFactory.create_row(field_name, field_spec, callback, parent, custom_widget)
            container_layout.addLayout(layout)

            setattr(parent, field_name, widget)
            setattr(parent, f'{field_name}Label', label)

            widgets[field_name] = widget

        return widgets

    @staticmethod
    def add_stretch(container_layout):
        container_layout.addStretch()

    @staticmethod
    def retranslate_from_spec(spec_group: Dict[str, Dict[str, Any]], parent: QWidget):
        for field_name, field_spec in spec_group.items():
            if 'i18n' in field_spec:
                label = getattr(parent, f'{field_name}Label', None)
                if label:
                    label.setText(i18n.t(field_spec['i18n']))
