import os
import sys

if hasattr(sys, 'frozen'):
    DLL_PATH = os.path.dirname(os.path.abspath(sys.executable))
else:
    DLL_PATH = os.path.join(os.curdir, 'dist')

if hasattr(sys, 'frozen'):
    LIB_PATH = os.path.join(DLL_PATH, 'lib')
else:
    LIB_PATH = os.path.join(os.curdir, 'lib')
