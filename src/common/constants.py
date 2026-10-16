import os
import sys
from importlib.metadata import PackageNotFoundError, version

IS_FROZEN = hasattr(sys, 'frozen')

APP_NAME = 'MouseFlight'

try:
    APP_VERSION = version(APP_NAME)
except PackageNotFoundError:
    APP_VERSION = ''

BASE_DIR = os.path.dirname(os.path.abspath(sys.executable)) if IS_FROZEN else os.curdir
DLL_PATH = os.path.dirname(os.path.abspath(sys.executable)) if IS_FROZEN else os.path.join(os.curdir, 'dist')
MODULES_PATH = 'modules'
EXTENSIONS_PATH = 'extensions'

FOV_RANGE = (0, 160)
