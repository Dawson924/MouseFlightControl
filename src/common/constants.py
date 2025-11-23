import os
import sys

import importlib_metadata

VERSION = importlib_metadata.version("MouseFlightControl")
IS_FROZEN = hasattr(sys, 'frozen')

if IS_FROZEN:
    DLL_PATH = os.path.dirname(os.path.abspath(sys.executable))
else:
    DLL_PATH = os.path.join(os.curdir, 'dist')

if IS_FROZEN:
    LUA_PATH = os.path.join(DLL_PATH, 'Lua')
else:
    LUA_PATH = os.path.join(os.curdir, 'Lua')

SCRIPT_PATH = 'scripts'
SCRIPT_INI_PATH = 'scripts.ini'

FOV_RANGE = (0, 160)
