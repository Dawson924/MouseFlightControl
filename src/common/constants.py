import os
import sys

IS_FROZEN = hasattr(sys, 'frozen')

APP_NAME = 'MouseFlightControl'
APP_VERSION = '0.16.3'

BASE_DIR = os.path.dirname(os.path.abspath(sys.executable)) if IS_FROZEN else os.curdir
DLL_PATH = (
    os.path.dirname(os.path.abspath(sys.executable))
    if IS_FROZEN
    else os.path.join(os.curdir, 'dist')
)
LUA_PATH = os.path.join(DLL_PATH if IS_FROZEN else os.curdir, 'Lua')
SCRIPT_PATH = 'scripts'
SCRIPT_INI_PATH = 'scripts.ini'

FOV_RANGE = (0, 160)
