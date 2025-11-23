import datetime
import os
import platform
import sys

from loguru import logger

from common.constants import IS_FROZEN

_init = True

LOG_FILE = 'full.log'
MAX_SIZE = 500 * 1024 * 1024


def get_format(record, console=True):
    end = '' if console else '\n'
    if record['level'].no >= 40:
        return (
            '<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> | '
            f'<level>{record["level"].name}</level> - '
            '<yellow>{name}.{function}:{line}</yellow>: '
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

def init_logger(app_name: str, app_version: str, debug: bool=True):
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
    python_version = sys.version.split()[0]
    pid = os.getpid()
    cwd = os.getcwd()
    startup_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")[:-3]

    logger.opt(colors=True).info(f"<bold><green>{'='*80}</green></bold>")
    logger.opt(colors=True).info(f"<bold><green>🚀 {app_name} - 启动成功</green></bold>")
    logger.opt(colors=True).info(f"<green>版本信息：</green> v{app_version}")
    logger.opt(colors=True).info(f"<green>启动时间：</green> {startup_time}")
    logger.opt(colors=True).info(f"<green>运行环境：</green> {system_info.system} {system_info.release} ({system_info.machine}) | Python {python_version} | PID: {pid} | 工作目录: {cwd}")
    logger.opt(colors=True).info(f"<green>日志文件：</green> {LOG_FILE}")
    logger.opt(colors=True).info(f"<bold><green>{'='*80}</green></bold>\n")
    if debug:
        logger.opt(colors=True).warning('<red>调试模式已开启</red>')

    _init = True


__all__ = ['logger', 'get_logger']