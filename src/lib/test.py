from connect.flight import FlightData
from lib.num import radians_to_degrees


def on_data_received(data: FlightData):
    print('Received from DCS:')
    print(f'Model: {data.model}')
    print(f'Heading: {radians_to_degrees(data.heading)}°')
    print(f'Pitch: {radians_to_degrees(data.pitch)}°')
    print(f'Bank: {radians_to_degrees(data.bank)}°')
    print(f'Airspeed: {data.airspeed}')
    print(f'Mach: {data.mach:.2f}')
    print(f'Elevation: {data.elevation}m')
    print('-' * 40)
