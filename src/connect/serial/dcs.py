import json
import socket
import threading
import time
from queue import Empty, Queue
from typing import Optional

from loguru import logger

from connect.flight import FlightConnect, FlightData
from connect.module import FlightSim


class DCSConnect(FlightConnect):
    def __init__(self, tcp_host='127.0.0.1', tcp_port=20070, udp_host='127.0.0.1', udp_port=20069, timeout=None):
        super().__init__(FlightSim.DCS)
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.timeout = timeout
        self.tcp_socket = None
        self.udp_socket = None
        self.udp_listener = None
        self.data_queue = Queue()
        self._create_sockets()

    def _create_sockets(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.settimeout(self.timeout)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(self.timeout)
        self.udp_socket.bind((self.udp_host, self.udp_port))

    def _create_data(self, raw_data):
        if raw_data:
            return FlightData.from_json(raw_data)
        return None

    def _send_tcp_data(self, data):
        if not self.tcp_socket:
            return

        json_data = json.dumps(data)
        self.tcp_socket.sendall(json_data.encode('utf-8'))

    def connect(self):
        try:
            if self.tcp_socket is None or self.udp_socket is None:
                self._create_sockets()

            if not self.udp_listener or not self.udp_listener.is_alive():
                self.connected = True
                self.udp_listener = threading.Thread(target=self._udp_listener)
                self.udp_listener.daemon = True
                self.udp_listener.start()
            logger.info('Connected successfully')
        except Exception as e:
            self.connected = False
            logger.exception(f'Unexpected error while connecting to DCS: {e}')
        finally:
            return self.connected

    def disconnect(self):
        self.connected = False
        if self.udp_listener and self.udp_listener.is_alive():
            self.udp_listener.join(timeout=1.0)
        if self.tcp_socket:
            self.tcp_socket.close()
            self.tcp_socket = None
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None

    def is_connected(self):
        return self.connected

    def get_data(self, timeout=None) -> Optional[FlightData]:
        if not self.connected:
            return None

        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                if self.data_queue.empty():
                    return self._create_data(data)
            return None
        except Empty:
            return None

    def perform_action(self, payload):
        data = {'type': 'action', 'payload': payload}
        self._send_tcp_data(data)

    @DeprecationWarning
    def start_listener(self, on_received):
        self.udp_listener = threading.Thread(target=self._udp_listener)
        self.udp_listener.daemon = True
        self.udp_listener.start()

    def _udp_listener(self):
        while self.connected:
            try:
                buffer, _ = self.udp_socket.recvfrom(4096)
                if buffer:
                    data = buffer.decode('utf-8')
                    self.data_queue.put(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self.connected:
                    logger.warning(f'Error in UDP listener: {e}')

                    try:
                        self.udp_socket.close()
                        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.udp_socket.settimeout(self.timeout)
                        self.udp_socket.bind((self.udp_host, self.udp_port))
                    except Exception as re:
                        logger.error(f'Failed to recreate UDP socket: {re}')
                        self.connected = False
                        break


# RUN TEST
if __name__ == '__main__':
    import datetime
    import time

    dcs_connect = DCSConnect()

    print('Connecting to DCS...')
    connected = dcs_connect.connect()
    print(f'Connection status: {connected}')

    if connected:
        print('\nTesting get_data... (press Ctrl+C to exit)')
        print('UDP validation enabled: checking data timestamps and consistency')

        last_data_time = None
        last_model = None
        consecutive_no_data = 0
        data_count = 0
        start_time = time.time()

        try:
            while True:
                current_time = time.time()
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')

                data = dcs_connect.get_data()

                if data:
                    data_count += 1
                    consecutive_no_data = 0

                    if data.model != last_model:
                        print(f'[{timestamp}] Model changed: {last_model} -> {data.model}')
                        last_model = data.model

                    if last_data_time:
                        interval = current_time - last_data_time
                        print(f'[{timestamp}] Data received: model={data.model}, interval={interval:.3f}s')
                    else:
                        print(f'[{timestamp}] First data received: model={data.model}')

                    last_data_time = current_time
                else:
                    consecutive_no_data += 1
                    if consecutive_no_data % 5 == 0:
                        print(f'[{timestamp}] No data received for {consecutive_no_data} consecutive attempts')

                if int(current_time - start_time) % 10 == 0 and int(current_time) != int(start_time):
                    elapsed = current_time - start_time
                    rate = data_count / elapsed if elapsed > 0 else 0
                    print(
                        f'\n[{timestamp}] Stats: {data_count} packets received in {elapsed:.1f}s ({rate:.2f} packets/s)'
                    )

                time.sleep(0.16)
        except KeyboardInterrupt:
            print('\nTesting is_connected...')
            print(f'Is connected: {dcs_connect.is_connected()}')

            print('\nDisconnecting...')
            dcs_connect.disconnect()
            print(f'Is connected after disconnect: {dcs_connect.is_connected()}')
    else:
        print('Failed to connect to DCS')
