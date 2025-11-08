import os
import sys

if hasattr(sys, 'frozen'):
    DLL_PATH = os.path.dirname(os.path.abspath(sys.executable))
else:
    DLL_PATH = os.path.join(os.curdir, 'dist')

if hasattr(sys, 'frozen'):
    LUA_PATH = os.path.join(DLL_PATH, 'Lua')
else:
    LUA_PATH = os.path.join(os.curdir, 'Lua')
