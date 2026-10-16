from typing import Optional

from connect.flight import FlightConnect, FlightParams
from connect.platform import Simulator


class MSFSConnect(FlightConnect):
    def __init__(self):
        super().__init__(Simulator.FS2020)
        self._flight_data: Optional[FlightParams] = None

    def connect(self):
        self.connected = False
        return self.connected

    def disconnect(self):
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def get_data(self, timeout=None) -> Optional[FlightParams]:
        return self._flight_data

    def perform_action(self, payload):
        pass
