import os
from typing import Tuple

import yaml

import i18n
from common.config import CONFIG_FILE, INPUT_FILE
from data.config import Config
from data.input import FlightInput
from lib.logger import logger

ConfigList = Tuple[Config, FlightInput]


def load_all() -> ConfigList:
    try:
        if not os.path.exists(CONFIG_FILE) or not os.path.exists(INPUT_FILE):
            raise FileExistsError()
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = Config.from_yaml(f)
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            flight = FlightInput.from_yaml(f)
        return (config, flight)
    except Exception as e:
        logger.exception(f'{i18n.t("ConfigLoadFailed")}: {e}')
        return Config(), FlightInput()


def save_all(configs: ConfigList) -> None:
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(configs[0], f, default_flow_style=False, sort_keys=False)
        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(configs[1], f, default_flow_style=False, sort_keys=False)
        logger.success(i18n.t('ConfigSaved'))
    except Exception as e:
        logger.error(f'{i18n.t("ConfigSaveFailed")}: {e}')
