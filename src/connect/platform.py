import os
from enum import Enum
from typing import Any, Dict, TypedDict

from configobj import ConfigObj, ConfigObjError
from loguru import logger
from validate import Validator

from common.constants import MODULES_PATH


class Simulator(str, Enum):
    DCS = 'DCS'
    FS2020 = 'MSFS2020'

    @property
    def full_name(self):
        names = {Simulator.DCS: 'DCS World', Simulator.FS2020: 'MSFS 2020'}
        return names[self]


class Module(TypedDict):
    id: str
    name: str
    data: Dict[str, Any]
    platform: Simulator
    aircraft_type: int
    is_grouped: bool
    image_path: str


LocalModules = Dict[str, Module]


MANIFEST_SPEC = {
    'Module': {
        'model': 'string(default=None)',
        'models': 'list(default=None)',
        'title': 'string',
        'platform': f'option({Simulator.DCS.value}, {Simulator.FS2020.value})',
    },
    'Data': {
        'flight_mode': 'integer(default=1, min=-1, max=3)',
        'camera_fov': 'integer(default=90, min=20, max=180)',
        'thrust_speed': 'integer(default=500, min=100, max=1000)',
        'rudder_speed': 'integer(default=120, min=100, max=1000)',
    },
}


def load_modules(base_dir: str = MODULES_PATH) -> LocalModules:
    registry = {}

    if not os.path.isdir(base_dir):
        logger.error('Directory {} does not exist', base_dir)
        return registry

    for dir, _, files in os.walk(base_dir):
        if 'manifest.ini' in files:
            manifest_path = os.path.join(dir, 'manifest.ini')

            try:
                manifest = ConfigObj(
                    manifest_path, encoding='utf-8', configspec=MANIFEST_SPEC, raise_errors=False, file_error=True
                )

                validator = Validator()
                valid = manifest.validate(validator)

                if valid is not True:
                    logger.error('Invalid manifest in {}: \n{}', manifest_path, valid)
                    continue

                if 'Module' not in manifest:
                    logger.error('Missing [Module] section in {}', manifest_path)
                    continue

                model = manifest['Module'].get('model')
                models = manifest['Module'].get('models')

                is_sub = False

                if model and models:
                    logger.error("Both 'model' and 'models' found in {}", manifest_path)
                    continue
                elif model:
                    mod_ids = [model]
                    is_sub = False
                elif models and isinstance(models, list):
                    mod_ids = [m.strip() for m in models if m.strip()]
                    is_sub = True
                else:
                    continue

                for mod_id in mod_ids:
                    if mod_id in registry:
                        logger.warning(
                            "Duplicate model key '{}' found, {} will overwrite existing configuration",
                            mod_id,
                            manifest_path,
                        )
                    if 'Module' in manifest:
                        sim_id = manifest['Module']['platform']
                        name = manifest['Module']['title']

                        module: Module = {
                            'id': mod_id,
                            'name': name,
                            'data': manifest['Data'],
                            'platform': Simulator(sim_id),
                            'aircraft_type': manifest['Data']['flight_mode'],
                            'is_grouped': is_sub,
                            'module_path': dir,
                            'entry_path': os.path.join(dir, 'main.py')
                            if os.path.isfile(os.path.join(dir, 'main.py'))
                            else None,
                            'image_path': os.path.join(dir, 'bg_image.jpg'),
                        }
                        registry[mod_id] = module

            except ConfigObjError as e:
                logger.exception('Invalid configuration format in {}: {}', manifest_path, str(e))
            except Exception as e:
                logger.exception('Error parsing {}: {}', manifest_path, str(e))

    return registry
