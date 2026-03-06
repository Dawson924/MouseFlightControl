import json
import socket
import threading
import time
from typing import Optional

from flightsim.connect import FlightConnect, FlightData


class DCSConnect(FlightConnect):
    def __init__(self, tcp_host='127.0.0.1', tcp_port=42070, udp_host='127.0.0.1', udp_port=42069):
        super().__init__()
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.udp_host, self.udp_port))
        self.running = False
        self.udp_listener = None
        self.data_received = None

    def _create_flight_data(self, raw_data):
        return FlightData.from_json(raw_data)

    def connect(self, listener=None):
        self.tcp_socket.connect((self.tcp_host, self.tcp_port))
        self.start_listener(listener)

    def disconnect(self):
        self.running = False
        if self.udp_listener and self.udp_listener.is_alive():
            self.udp_listener.join()
        self.tcp_socket.close()
        self.udp_socket.close()

    def send_command(self, payload):
        data = {'type': 'actions', 'payload': payload}
        self._send_tcp_data(data)

    def start_listener(self, callback=None):
        self.data_received = callback
        self.running = True
        self.udp_listener = threading.Thread(target=self._udp_listen_loop)
        self.udp_listener.daemon = True
        self.udp_listener.start()

    def _send_tcp_data(self, data):
        json_data = json.dumps(data)
        self.tcp_socket.sendall(json_data.encode('utf-8'))

    def _udp_listen_loop(self):
        while self.running:
            try:
                buffer, _ = self.udp_socket.recvfrom(4096)
                if buffer:
                    data = self._create_flight_data(buffer.decode('utf-8'))
                    if self.data_received:
                        self.data_received(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    raise e

    def get_udp_data(self, timeout=None) -> Optional[FlightData]:
        self.udp_socket.settimeout(timeout)
        try:
            data, addr = self.udp_socket.recvfrom(4096)
            return self._create_flight_data(json.loads(data.decode('utf-8'))) if data else None
        except socket.timeout:
            return None


if __name__ == '__main__':

    def on_data_received(data: FlightData):
        print('Received from DCS:')
        print(f'Model: {data.module}')
        print(f'Heading: {data.heading}°')
        print(f'Pitch: {data.pitch}°')
        print(f'Bank: {data.bank}°')
        print(f'Airspeed: {data.airspeed} knots')
        print(f'Coords: {data.latitude}, {data.longitude}')
        print(f'Elevation: {data.elevation}m')
        print('-' * 40)
        time.sleep(0.25)

    communicator = DCSConnect()
    try:
        communicator.connect(on_data_received)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        communicator.disconnect()
