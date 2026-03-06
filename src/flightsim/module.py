import os
from enum import Enum
from typing import Any, Dict

from configobj import ConfigObj, ConfigObjError
from validate import Validator
from loguru import logger

from common.constants import MODULES_PATH


class FlightSim(str, Enum):
    DCS = 'DCS'
    FS2020 = 'MSFS2020'

    @property
    def full_name(self):
        names = {FlightSim.DCS: 'DCS World', FlightSim.FS2020: 'Microsoft Flight Simulator'}
        return names[self]


MODULE_SPEC = {
    'Manifest': {
        'model': 'string()',
        'title': 'string()',
        'platform': 'option("DCS", "MSFS2020")',
        'connect': 'option("serial", "simconnect", "dcs-bios")',
    },
    'Data': {
        'flight_mode': 'integer(default=1, min=-1, max=2)',
        'camera_fov': 'integer(default=90, min=20, max=180)',
        'throttle_speed': 'integer(default=250, min=100, max=1000)',
        'collective_speed': 'integer(default=140, min=100, max=1000)',
        'pedals_speed': 'integer(default=120, min=100, max=1000)',
        'throttle_increase': 'string(default="x")',
        'throttle_decrease': 'string(default="z")',
    },
}


def load_modules(base_dir: str = MODULES_PATH) -> Dict[str, Dict[str, Any]]:
    map = {}

    if not os.path.isdir(base_dir):
        logger.error('Directory {} does not exist', base_dir)
        return map

    for root, _, files in os.walk(base_dir):
        if 'module.ini' in files:
            ini_file_path = os.path.join(root, 'module.ini')

            try:
                config = ConfigObj(
                    ini_file_path, encoding='utf-8', configspec=MODULE_SPEC, raise_errors=False, file_error=True
                )

                validator = Validator()
                config.validate(validator)

                if 'Manifest' in config:
                    model = config['Manifest']['model']
                    key = model
                else:
                    key = os.path.basename(root)

                if key in map:
                    logger.warning(
                        "Duplicate model key '{}' found, {} will overwrite existing configuration", key, ini_file_path
                    )
                map[key] = (root, dict(config))

            except ConfigObjError as e:
                logger.exception('Invalid configuration format in {}: {}', ini_file_path, str(e))
            except Exception as e:
                logger.exception('Error parsing {}: {}', ini_file_path, str(e))

    return map