from typing import Any, Dict

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QVBoxLayout, QWidget

from data.config import ConfigData
from data.flight import FlightData
from lib.screen import ScreenGeometry


class AbstractPage(QWidget):
    state_changed = Signal()

    def __init__(self, win: ScreenGeometry, config: ConfigData, flight: FlightData, parent=None):
        super().__init__(parent)

        self.win = win

        self.config = config
        self.flight = flight

        # Initialize UI elements dictionary
        self.ui_elements: Dict[str, Any] = {}

        # Create main page layout
        self.page_layout = QVBoxLayout(self)
        self.page_layout.setSpacing(10)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

    def set_config(self, key: str, value: Any):
        """Set configuration value."""
        self.config.set(key, value)
        if hasattr(self, 'ui_elements') and key in self.ui_elements:
            self.update_state(key, type(value))

    def set_flight_data(self, key: str, value: Any):
        """Set flight data value."""
        self.flight.set(key, value)
        if hasattr(self, 'ui_elements') and key in self.ui_elements:
            self.update_state(key, type(value))

    def update_state(self, field: str, setter_type: type):
        """
        Update UI element state based on data.

        Args:
            field: Name of the field to update
            setter_type: Type of the setter function (str, int, bool, etc.)
        """
        if field not in self.ui_elements:
            return

        widget = getattr(self, field)
        method_name = self._get_setter_method_name(setter_type)
        method = getattr(widget, method_name, None)

        # Try to get value from config first, then flight data
        arg = self.config.get(field) or self.flight.get(field)

        if arg is not None and method and callable(method):
            # Convert argument to the expected type
            converted_arg = setter_type(arg)
            method(converted_arg)

    def _get_setter_method_name(self, setter_type: type) -> str:
        """
        Get appropriate setter method name based on the data type.

        Args:
            setter_type: Type of the setter function

        Returns:
            Method name to use for setting the value
        """
        if setter_type is bool:
            return 'setChecked'
        elif setter_type is str:
            return 'setText'
        elif setter_type is int or setter_type is float:
            return 'setValue'
        else:
            # Default to setText for unknown types
            return 'setText'

    def update_states(self):
        """Update all UI elements based on current data values."""
        for field, definition in self.ui_elements.items():
            if len(definition) > 0:
                setter = definition[0]
                self.update_state(field, setter)

    def retranslate_ui(self):
        """Override this method to handle UI translation updates."""
        pass
