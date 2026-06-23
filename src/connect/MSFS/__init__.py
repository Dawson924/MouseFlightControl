import threading
from typing import Optional

from loguru import logger
from SimConnect import AircraftRequests, SimConnect

from connect.flight import FlightConnect, FlightData
from connect.module import FlightSim


class MSFSConnect(FlightConnect):
    def __init__(self):
        super().__init__(FlightSim.FS2020)
        self.simconnect: Optional[SimConnect] = None
        self.aircraft_requests: Optional[AircraftRequests] = None
        self._data_lock = threading.Lock()
        self._flight_data: Optional[FlightData] = None
        self._listener_thread: Optional[threading.Thread] = None

    def connect(self):
        try:
            self.simconnect = SimConnect()
            self.aircraft_requests = AircraftRequests(self.simconnect)
            self.connected = True

            self._listener_thread = threading.Thread(target=self._data_listener)
            self._listener_thread.daemon = True
            self._listener_thread.start()
            logger.info('Connected successfully')
        except Exception as e:
            self.connected = False
            logger.exception(f'Failed to connect to MSFS: {e}')
        finally:
            return self.connected

    def disconnect(self):
        self.connected = False
        if self.simconnect:
            try:
                self.simconnect.exit()
            except Exception as e:
                logger.warning(f'Error closing SimConnect: {e}')
            self.simconnect = None

        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1.0)

        logger.info('Disconnected from MSFS')

    def is_connected(self) -> bool:
        return self.connected

    def get_data(self, timeout=None) -> Optional[FlightData]:
        with self._data_lock:
            return self._flight_data

    def perform_action(self, payload):
        pass

    def _data_listener(self):
        while self.connected and self.simconnect and self.aircraft_requests:
            try:
                raw_data = self._read_flight_data()
                if raw_data:
                    with self._data_lock:
                        self._flight_data = FlightData(raw_data)
            except Exception as e:
                if self.connected:
                    logger.warning(f'Error reading MSFS data: {e}')
                    self.connected = False
                break

    def _read_flight_data(self) -> Optional[dict]:
        try:
            title = self.aircraft_requests.StringData.get('TITLE')
            latitude = self.aircraft_requests.PositionandSpeedData.get('PLANE_LATITUDE')
            longitude = self.aircraft_requests.PositionandSpeedData.get('PLANE_LONGITUDE')
            altitude = self.aircraft_requests.PositionandSpeedData.get('PLANE_ALTITUDE')
            heading = self.aircraft_requests.PositionandSpeedData.get('PLANE_HEADING_DEGREES_TRUE')
            pitch = self.aircraft_requests.PositionandSpeedData.get('PLANE_PITCH_DEGREES')
            bank = self.aircraft_requests.PositionandSpeedData.get('PLANE_BANK_DEGREES')
            indicated_airspeed = self.aircraft_requests.FlightInstrumentationData.get('AIRSPEED_INDICATED')
            true_airspeed = self.aircraft_requests.FlightInstrumentationData.get('AIRSPEED_TRUE')
            mach = self.aircraft_requests.FlightInstrumentationData.get('AIRSPEED_MACH')

            if latitude is None and longitude is None:
                return None

            return {
                'module': title or '',
                'heading': self._rad_to_deg(heading) if heading else 0.0,
                'pitch': self._rad_to_deg(pitch) if pitch else 0.0,
                'bank': self._rad_to_deg(bank) if bank else 0.0,
                'yaw': 0.0,
                'airspeed': {
                    'indicated': indicated_airspeed if indicated_airspeed else 0.0,
                    'true': true_airspeed if true_airspeed else 0.0,
                },
                'mach': mach if mach else 0.0,
                'coords': {
                    'lat': latitude if latitude else 0.0,
                    'long': longitude if longitude else 0.0,
                },
                'elev': altitude if altitude else 0.0,
                'mech': {},
            }
        except Exception as e:
            logger.warning(f'Error reading flight data: {e}')
            return None

    def _rad_to_deg(self, radians: float) -> float:
        return radians * 57.29577951308232
