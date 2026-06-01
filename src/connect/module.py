import os
from enum import Enum
from typing import Any, Dict, List, TypedDict, Union

from configobj import ConfigObj, ConfigObjError
from loguru import logger
from validate import Validator

from common.constants import MODULES_PATH
from controller.control import FixedWingController, HelicopterController
from controller.manager import FlightControllers


class ModuleConfig(TypedDict):
    model: Union[str, List[str]]
    title: str
    platform: str
    connect: str


class ModuleConfig(TypedDict):
    Module: ModuleConfig
    Data: Dict[str, Any]


class FlightSim(str, Enum):
    DCS = 'DCS'
    FS2020 = 'MSFS2020'

    @property
    def full_name(self):
        names = {FlightSim.DCS: 'DCS World', FlightSim.FS2020: 'MSFS 2020'}
        return names[self]


class FlightModule(TypedDict):
    id: str
    name: str
    image_path: str
    control: int
    platform: FlightSim
    data: Dict[str, Any]


FlightModules = Dict[str, FlightModule]


MODULE_SPEC = {
    'Module': {
        'model': 'string(default=None)',
        'models': 'list(default=None)',
        'title': 'string',
        'platform': f'option({FlightSim.DCS.value}, {FlightSim.FS2020.value})',
        'connect': 'option("serial", "simconnect", "dcs-bios")',
    },
    'Data': {
        'flight_mode': 'integer(default=1, min=-1, max=2)',
        'camera_fov': 'integer(default=90, min=20, max=180)',
        'thrust_speed': 'integer(default=500, min=100, max=1000)',
        'collective_speed': 'integer(default=140, min=100, max=1000)',
        'rudder_speed': 'integer(default=120, min=100, max=1000)',
    },
}


def load_modules(base_dir: str = MODULES_PATH) -> FlightModules:
    registry = {}

    if not os.path.isdir(base_dir):
        logger.error('Directory {} does not exist', base_dir)
        return registry

    for dir, _, files in os.walk(base_dir):
        if 'manifest.ini' in files:
            ini_file_path = os.path.join(dir, 'manifest.ini')

            try:
                manifest = ConfigObj(
                    ini_file_path, encoding='utf-8', configspec=MODULE_SPEC, raise_errors=False, file_error=True
                )

                validator = Validator()
                valid = manifest.validate(validator)

                if valid is not True:
                    logger.error('Invalid manifest in {}: \n{}', ini_file_path, valid)
                    continue

                if 'Module' not in manifest:
                    logger.error('Missing [Module] section in {}', ini_file_path)
                    continue

                model = manifest['Module'].get('model')
                models = manifest['Module'].get('models')

                if model and models:
                    logger.warning("Both 'model' and 'models' found in {}, using 'model' only", ini_file_path)
                    mod_ids = [model]
                elif model:
                    mod_ids = [model]
                elif models and isinstance(models, list):
                    mod_ids = [m.strip() for m in models if m.strip()]
                else:
                    continue

                for mod_id in mod_ids:
                    if mod_id in registry:
                        logger.warning(
                            "Duplicate model key '{}' found, {} will overwrite existing configuration",
                            mod_id,
                            ini_file_path,
                        )
                    if 'Module' in manifest:
                        sim_id = manifest['Module']['platform']
                        name = manifest['Module']['title']

                        module: FlightModule = {
                            'id': mod_id,
                            'name': name,
                            'platform': FlightSim(sim_id),
                            'control': manifest['Data']['flight_mode'],
                            'data': manifest['Data'],
                            'image_path': os.path.join(dir, 'bg_image.jpg'),
                        }
                        registry[mod_id] = module

            except ConfigObjError as e:
                logger.exception('Invalid configuration format in {}: {}', ini_file_path, str(e))
            except Exception as e:
                logger.exception('Error parsing {}: {}', ini_file_path, str(e))

    return registry


controllers = FlightControllers()

controllers.register(
    1,
    FixedWingController,
    {'name': 'Fixed Wing'},
)
controllers.register(
    2,
    HelicopterController,
    {'name': 'Helicopter'},
)
