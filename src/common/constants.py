import os
import sys

if hasattr(sys, 'frozen'):
    DLL_PATH = os.path.dirname(os.path.abspath(sys.executable))
else:
    DLL_PATH = os.path.join(os.curdir, 'dist')

if hasattr(sys, 'frozen'):
    LUA_LIBS_PATH = os.path.join(DLL_PATH, 'lua_libs')
else:
    LUA_LIBS_PATH = os.path.join(os.curdir, 'lua_libs')
