import os
from enum import Enum
from typing import Any, Dict, Tuple, TypedDict

from configobj import ConfigObj, ConfigObjError
from loguru import logger
from validate import Validator

from common.constants import MODULES_PATH
from controller.control import FixedWingController, HelicopterController
from controller.manager import ControllerManager


class ModuleConfig(TypedDict):
    model: str
    title: str
    platform: str
    connect: str


class ModuleConfig(TypedDict):
    Module: ModuleConfig
    Data: Dict[str, Any]


ModuleData = Dict[str, Tuple[str, ModuleConfig]]


class FlightSim(str, Enum):
    DCS = 'DCS'
    FS2020 = 'MSFS2020'

    @property
    def full_name(self):
        names = {FlightSim.DCS: 'DCS World', FlightSim.FS2020: 'MSFS 2020'}
        return names[self]


MODULE_SPEC = {
    'Module': {
        'model': 'string()',
        'title': 'string()',
        'platform': f'option({FlightSim.DCS.value}, {FlightSim.FS2020.value})',
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


def load_modules(base_dir: str = MODULES_PATH) -> ModuleData:
    map = {}

    if not os.path.isdir(base_dir):
        logger.error('Directory {} does not exist', base_dir)
        return map

    for root, _, files in os.walk(base_dir):
        if 'manifest.ini' in files:
            ini_file_path = os.path.join(root, 'manifest.ini')

            try:
                manifest = ConfigObj(
                    ini_file_path, encoding='utf-8', configspec=MODULE_SPEC, raise_errors=False, file_error=True
                )

                validator = Validator()
                valid = manifest.validate(validator)

                if valid is not True:
                    logger.error('Invalid manifest in {}: \n{}', ini_file_path, valid)
                    continue

                if 'Module' in manifest:
                    model = manifest['Module']['model']
                    key = model
                else:
                    key = os.path.basename(root)

                if key in map:
                    logger.warning(
                        "Duplicate model key '{}' found, {} will overwrite existing configuration", key, ini_file_path
                    )
                map[key] = (root, dict(manifest))

            except ConfigObjError as e:
                logger.exception('Invalid configuration format in {}: {}', ini_file_path, str(e))
            except Exception as e:
                logger.exception('Error parsing {}: {}', ini_file_path, str(e))

    return map


controller_manager = ControllerManager()

controller_manager.register(
    1,
    FixedWingController,
    {'name': 'Fixed Wing', 'options': FixedWingController.get_options(), 'i18n': FixedWingController.get_i18n()},
)
controller_manager.register(
    2,
    HelicopterController,
    {'name': 'Helicopter', 'options': HelicopterController.get_options(), 'i18n': HelicopterController.get_i18n()},
)
