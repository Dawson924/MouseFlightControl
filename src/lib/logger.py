import datetime
import os
import platform

from loguru import logger

import i18n
from common.constants import APP_VERSION, IS_FROZEN

_init = False

LOG_FILE = 'full.log'
MAX_SIZE = 500 * 1024 * 1024


def get_format(record, console=True):
    end = '' if console else '\n'
    if record['level'].no >= 40:
        return (
            '<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> | '
            f'<level>{record["level"].name}</level> - '
            '<level>{message}</level>\n{exception}' + end
        )
    else:
        return (
            '<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> | '
            f'<level>{record["level"].name}</level> - '
            '<level>{message}</level>' + end
        )


def should_rotate(_, file):
    file_path = file.name
    if os.path.exists(file_path) and os.path.getsize(file_path) > MAX_SIZE:
        with open(file_path, 'w', encoding='utf-8'):
            pass
        return True
    return False


def get_logger():
    if not _init:
        raise RuntimeError('Call initialization before using Logger instance')
    else:
        return logger


def init_logger():
    logger.remove()

    logger.add(
        sink=print,
        format=lambda r: get_format(r, console=True),
        colorize=True,
        level='DEBUG',
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=False,
    )

    if IS_FROZEN:
        logger.add(
            sink=LOG_FILE,
            format=lambda r: get_format(r, console=False),
            rotation=should_rotate,
            colorize=False,
            level='INFO',
            backtrace=True,
            diagnose=True,
            enqueue=True,
            catch=False,
        )

    system_info = platform.uname()
    pid = os.getpid()
    cwd = os.getcwd()
    startup_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]

    def func(log):
        logger.opt(colors=True).info(f'<bold><green>{"=" * 80}</green></bold>')
        logger.opt(colors=True).info(
            f'<bold><green>🚀 {i18n.t("MouseFlight")} - {i18n.t("StartupSuccessful")}</green></bold>'
        )
        logger.opt(colors=True).info(
            f'<green>{i18n.t("VersionInfo")}: </green> v{APP_VERSION}'
        )
        logger.opt(colors=True).info(
            f'<green>{i18n.t("StartupTime")}: </green> {startup_time}'
        )
        logger.opt(colors=True).info(
            f'<green>{i18n.t("RuntimeEnv")}: </green> {system_info.system} {system_info.release} ({system_info.machine}) | PID: {pid} | {cwd}'
        )
        logger.opt(colors=True).info(f'<green>{i18n.t("LogFile")}: </green> {LOG_FILE}')
        log(logger)
        logger.opt(colors=True).info(f'<bold><green>{"=" * 80}</green></bold>\n')

    _init = True
    logger.done = func


__all__ = ['logger', 'get_logger']
