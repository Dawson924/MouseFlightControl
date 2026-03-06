import os
from typing import Tuple

import yaml

import i18n
from common.config import CONFIG_FILE, FLIGHT_FILE
from data.config import ConfigData
from data.flight import FlightData
from loguru import logger

ConfigList = Tuple[ConfigData, FlightData]


def load_all_data() -> ConfigList:
    try:
        if not os.path.exists(CONFIG_FILE) or not os.path.exists(FLIGHT_FILE):
            raise FileExistsError()
        config = ConfigData.from_yaml(file_path=CONFIG_FILE)
        flight = FlightData.from_yaml(file_path=FLIGHT_FILE)
        return (config, flight)
    except Exception as e:
        logger.exception(f'{i18n.t("ConfigLoadFailed")}: {e}')
        return ConfigData(), FlightData()


def save_all_data(configs: ConfigList) -> None:
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(configs[0], f, default_flow_style=False, sort_keys=False)
        with open(FLIGHT_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(configs[1], f, default_flow_style=False, sort_keys=False)
        logger.success(i18n.t('ConfigSaved'))
    except Exception as e:
        logger.error(f'{i18n.t("ConfigSaveFailed")}: {e}')