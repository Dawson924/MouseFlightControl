import os
import sys

if hasattr(sys, 'frozen'):
    BINARY_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BINARY_DIR = os.path.join(os.curdir, 'dist')
