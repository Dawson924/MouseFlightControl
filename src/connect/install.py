import os
import shutil
from abc import ABC, abstractmethod
from typing import List, Optional

from loguru import logger

from connect.module import FlightSim

DCS_FOLDERS = ['DCS', 'DCS.openbeta', 'DCS World', 'DCS World OpenBeta']
EXPORT_DIRECTORY = 'FlightConnect'
CONNECT_SCRIPT = 'connect.lua'
EXPORT_LUA = 'Export.lua'


class AbstractInstaller(ABC):
    def __init__(self, platform: FlightSim):
        self.platform = platform

    @abstractmethod
    def get_paths(self) -> List[str]:
        pass

    @abstractmethod
    def is_installed(self, install_path: str) -> bool:
        pass

    @abstractmethod
    def install(self, install_path: str) -> bool:
        pass


class DCSInstaller(AbstractInstaller):
    def __init__(self):
        super().__init__(FlightSim.DCS)

    def get_paths(self) -> List[str]:
        saved_games = self._get_saved_games_path()
        if not saved_games:
            return []

        paths = []
        for folder in DCS_FOLDERS:
            full_path = os.path.join(saved_games, folder)
            if os.path.isdir(full_path):
                paths.append(full_path)

        return paths

    def _get_saved_games_path(self) -> Optional[str]:
        user_dir = os.path.expanduser('~')
        if not user_dir:
            return None

        saved_games = os.path.join(user_dir, 'Saved Games')
        if os.path.isdir(saved_games):
            return saved_games

        logger.warning(f'Saved Games folder not found at {saved_games}')
        return None

    def _get_connect_lua_template(self) -> str:
        return os.path.join(os.path.dirname(__file__), 'DCS', CONNECT_SCRIPT)

    def _get_export_lua_template(self) -> str:
        return os.path.join(os.path.dirname(__file__), 'DCS', EXPORT_LUA)

    def _install_connect_lua(self, install_path: str) -> bool:
        try:
            scripts_dir = os.path.join(install_path, 'Scripts')
            flight_connect_dir = os.path.join(scripts_dir, EXPORT_DIRECTORY)

            os.makedirs(flight_connect_dir, exist_ok=True)

            source_path = self._get_connect_lua_template()
            target_path = os.path.join(flight_connect_dir, CONNECT_SCRIPT)

            shutil.copy2(source_path, target_path)
            logger.info(f'{CONNECT_SCRIPT} installed to {target_path}')
            return True
        except Exception as e:
            logger.error(f'Failed to install {CONNECT_SCRIPT}: {e}')
            return False

    def _has_entry(self, export_lua_path: str) -> bool:
        try:
            if not os.path.exists(export_lua_path):
                return False

            with open(export_lua_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return EXPORT_DIRECTORY in content or CONNECT_SCRIPT in content
        except Exception as e:
            logger.error(f'Failed to check {EXPORT_LUA}: {e}')
            return False

    def _install_export_entry(self, install_path: str) -> bool:
        try:
            export_lua_path = os.path.join(install_path, 'Scripts', EXPORT_LUA)
            template_path = self._get_export_lua_template()

            if self._has_entry(export_lua_path):
                logger.info(f'{EXPORT_DIRECTORY} entry already exists in {EXPORT_LUA}')
                return True

            with open(template_path, 'r', encoding='utf-8') as f:
                export_entry = f.read().strip()

            if os.path.exists(export_lua_path):
                with open(export_lua_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if content and not content.endswith('\n'):
                    content += '\n'

                content += export_entry + '\n'

                with open(export_lua_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f'Added {EXPORT_DIRECTORY} entry to existing {EXPORT_LUA} at {export_lua_path}')
            else:
                shutil.copy2(template_path, export_lua_path)
                logger.info(f'Created {EXPORT_LUA} at {export_lua_path}')

            return True
        except Exception as e:
            logger.error(f'Failed to update {EXPORT_LUA}: {e}')
            return False

    def is_installed(self, install_path: str) -> bool:
        connect_path = os.path.join(install_path, 'Scripts', EXPORT_DIRECTORY, CONNECT_SCRIPT)
        export_path = os.path.join(install_path, 'Scripts', EXPORT_LUA)

        if not os.path.exists(connect_path):
            return False

        if not self._has_entry(export_path):
            return False

        return True

    def install(self, install_path: str) -> bool:
        logger.info(f'Starting {self.platform.full_name} installation to {install_path}')

        if not self._install_connect_lua(install_path):
            return False

        if not self._install_export_entry(install_path):
            return False

        logger.info(f'{self.platform.full_name} installation completed successfully')
        return True


class MSFSInstaller(AbstractInstaller):
    MSFS_PATHS = [
        r'C:\Program Files\WindowsApps\Microsoft.FlightSimulator_1*',
        r'C:\Program Files (x86)\Steam\steamapps\common\Microsoft Flight Simulator',
    ]

    def __init__(self):
        super().__init__(FlightSim.FS2020)

    def get_paths(self) -> List[str]:
        paths = []
        for pattern in self.MSFS_PATHS:
            if '*' in pattern:
                parent = os.path.dirname(pattern)
                prefix = os.path.basename(pattern).rstrip('*')
                if os.path.isdir(parent):
                    for folder in os.listdir(parent):
                        if folder.startswith(prefix):
                            paths.append(os.path.join(parent, folder))
            else:
                if os.path.isdir(pattern):
                    paths.append(pattern)
        return paths

    def is_installed(self, install_path: str) -> bool:
        if not install_path or not os.path.isdir(install_path):
            return False

        exe_path = os.path.join(install_path, 'FlightSimulator.exe')
        return os.path.isfile(exe_path)

    def install(self, install_path: str) -> bool:
        return True


def get_installer(platform: FlightSim) -> AbstractInstaller:
    installers = {
        FlightSim.DCS: DCSInstaller,
        FlightSim.FS2020: MSFSInstaller,
    }

    installer_class = installers.get(platform)
    if not installer_class:
        raise ValueError(f'Unsupported platform: {platform}')

    return installer_class()


def is_installed(platform: FlightSim) -> bool:
    installer = get_installer(platform)
    paths = installer.get_paths()

    for path in paths:
        if installer.is_installed(path):
            return True

    return False


def install(platform: FlightSim) -> Optional[str]:
    installer = get_installer(platform)
    paths = installer.get_paths()

    if not paths:
        logger.warning(f'No {platform.full_name} UserData path found')
        return None

    for path in paths:
        if installer.install(path):
            return path

    return None


def get_install_paths(platform: FlightSim) -> List[str]:
    installer = get_installer(platform)
    return installer.get_paths()
