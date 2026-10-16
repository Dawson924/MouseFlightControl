import json
import os
from typing import Any, Dict

CONFIG_DIR = 'config'


def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def load_plugin_config(plugin_id: str) -> Dict[str, Any]:
    ensure_config_dir()

    config_path = os.path.join(CONFIG_DIR, f'{plugin_id}.json')

    if not os.path.isfile(config_path):
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        from loguru import logger

        logger.warning(f'Failed to load config for {plugin_id}: {e}')
        return {}


def save_plugin_config(plugin_id: str, data: Dict[str, Any]) -> None:
    ensure_config_dir()

    config_path = os.path.join(CONFIG_DIR, f'{plugin_id}.json')

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        from loguru import logger

        logger.error(f'Failed to save config for {plugin_id}: {e}')


def delete_plugin_config(plugin_id: str) -> bool:
    config_path = os.path.join(CONFIG_DIR, f'{plugin_id}.json')

    if os.path.isfile(config_path):
        try:
            os.remove(config_path)
            return True
        except OSError as e:
            from loguru import logger

            logger.error(f'Failed to delete config for {plugin_id}: {e}')
            return False

    return False


def list_plugin_configs() -> Dict[str, Dict[str, Any]]:
    ensure_config_dir()

    configs = {}

    for filename in os.listdir(CONFIG_DIR):
        if filename.endswith('.json'):
            plugin_id = filename[:-5]
            configs[plugin_id] = load_plugin_config(plugin_id)

    return configs
