from PySide2.QtCore import Qt
from PySide2.QtWidgets import QComboBox, QLineEdit, QSpinBox

from common.win32 import KEYS


class LineEdit(QLineEdit):
    def __init__(self, parent=None, min_width=100, max_width=100):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 10px;
                background: white;
                min-width: %spx;
                max-width: %spx;
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
            % (min_width, max_width)
        )


class SpinBox(QSpinBox):
    def __init__(self, parent=None, min_width=100, max_width=100):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QSpinBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 10px;
                background: white;
                min-width: %spx;
                max-width: %spx;
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
            % (min_width, max_width)
        )
        self.setMinimum(0)
        self.setMaximum(1000000)


class ComboBox(QComboBox):
    def __init__(self, parent=None, min_width=100):
        super().__init__(parent)
        self.setMinimumWidth(min_width)
        self.setStyleSheet(
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


class KeybindEdit(QLineEdit):
    def __init__(self, parent=None, min_width=100, max_width=100):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 10px;
                background: white;
                min-width: %spx;
                max-width: %spx;
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
            % (min_width, max_width)
        )
        self.is_recording = False
        self.setText('Press key...')
        self.setReadOnly(True)

    def keyPressEvent(self, event):
        if not self.is_recording:
            super().keyPressEvent(event)
            return

        key_event = event.key()
        key_name = self.keyToString(key_event)
        if key_name:
            key = key_name
        else:
            if key_event >= Qt.Key_A and key_event <= Qt.Key_Z:
                key = chr(key_event).upper()
            else:
                key = event.text()
                if key:
                    key = key.upper()

        modifiers = []
        if event.modifiers() & Qt.ControlModifier:
            modifiers.append('Ctrl')
        if event.modifiers() & Qt.ShiftModifier:
            modifiers.append('Shift')
        if event.modifiers() & Qt.AltModifier:
            modifiers.append('Alt')

        if key:
            if modifiers:
                keybind = '+'.join(modifiers) + '+' + key
            else:
                keybind = key
            self.setText(keybind)
            self.is_recording = False
        event.accept()

    def keyToString(self, key):
        return KEYS.get(key, '')

    def mousePressEvent(self, event):
        self.is_recording = True
        self.setText('Recording...')

    def event(self, event):
        if event.type() == event.KeyPress:
            self.keyPressEvent(event)
            return True
        return super().event(event)
