import json
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, TypeVar

from connect.module import FlightSim

T = TypeVar('T', bound='FlightData')


class FlightData:
    def __init__(self, raw_data: Dict):
        self.model: Optional[str] = raw_data.get('module')
        self.heading: Optional[float] = float(raw_data.get('heading', 0.0))
        self.pitch: Optional[float] = float(raw_data.get('pitch', 0.0))
        self.bank: Optional[float] = float(raw_data.get('bank', 0.0))
        self.yaw: Optional[float] = float(raw_data.get('yaw', 0.0))
        self.airspeed: Optional[float] = dict(raw_data.get('airspeed', {}))
        self.mach: Optional[float] = float(raw_data.get('mach', 0.0))
        self.latitude: Optional[float] = float(raw_data.get('coords', {}).get('lat', 0.0))
        self.longitude: Optional[float] = float(raw_data.get('coords', {}).get('long', 0.0))
        self.elevation: Optional[float] = float(raw_data.get('elev', 0.0))
        self.mech = dict(raw_data.get('mech', {}))

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        raw_data = json.loads(json_str)
        return cls(raw_data)

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> T:
        return cls(data)

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class FlightConnect(ABC):
    def __init__(self, platform: FlightSim):
        self.platform = platform
        self.connected = False

    def _create_data(self, raw_data: Dict) -> FlightData:
        return FlightData(raw_data)

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def perform_action(self, payload):
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        return self.connected
