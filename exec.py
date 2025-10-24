import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent

if __name__ == '__main__':
    argv = sys.argv
    try:
        if argv.__len__() >= 2:
            script_name = argv[1]
            exec_path = BASE_DIR / 'tasks' / script_name.__add__('.bat')
            args = " ".join(argv[2:])
            print('Target:', exec_path)
            if argv.__len__() > 2:
                os.system(f'"{exec_path.__str__()}" {args}')
            else:
                os.system(exec_path.__str__())
        print('\nFinished!')

    except:
        print('\nError occured while executing', argv.__str__())
