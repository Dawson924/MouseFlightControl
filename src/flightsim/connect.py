import json
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, TypeVar

T = TypeVar('T', bound='FlightData')


class FlightData:
    def __init__(self, raw_data: Dict):
        self.module: Optional[str] = raw_data.get('module')
        self.heading: Optional[float] = float(raw_data.get('heading', 0.0)) if raw_data.get('heading') else None
        self.pitch: Optional[float] = float(raw_data.get('pitch', 0.0)) if raw_data.get('pitch') else None
        self.bank: Optional[float] = float(raw_data.get('bank', 0.0)) if raw_data.get('bank') else None
        self.yaw: Optional[float] = float(raw_data.get('yaw', 0.0)) if raw_data.get('yaw') else None
        self.airspeed: Optional[float] = float(raw_data.get('airspeed', 0.0)) if raw_data.get('airspeed') else None
        self.mach: Optional[float] = float(raw_data.get('mach', 0.0)) if raw_data.get('mach') else None
        self.latitude: Optional[float] = (
            float(raw_data.get('coords', {}).get('lat', 0.0)) if raw_data.get('coords', {}).get('lat') else None
        )
        self.longitude: Optional[float] = (
            float(raw_data.get('coords', {}).get('long', 0.0)) if raw_data.get('coords', {}).get('long') else None
        )
        self.elevation: Optional[float] = float(raw_data.get('elev', 0.0)) if raw_data.get('elev') else None

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
    def __init__(self, platform: str):
        self.platform = platform

    def _create_flight_data(self, raw_data: Dict) -> FlightData:
        return FlightData(raw_data)

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send_command(self, payload):
        pass
