import importlib.util
import os
import sys
from typing import List

PROJECT_ROOT = os.getcwd()
sys.path.insert(0, PROJECT_ROOT)
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
sys.path.insert(0, SRC_DIR)


def run_script(script_path: str, args: List[str] = None):
    args = args or []

    abs_script_path = os.path.abspath(script_path)
    if not os.path.exists(abs_script_path):
        raise FileNotFoundError(abs_script_path)

    original_argv = sys.argv.copy()
    try:
        sys.argv = [abs_script_path] + args

        spec = importlib.util.spec_from_file_location('__main__', abs_script_path)
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)
    finally:
        sys.argv = original_argv


def dev():
    run_script('exec.py', ['uic'])
    run_script(os.path.join('src', 'main.py'))


def build():
    run_script('exec.py', ['uic'])
    run_script('pyinstaller.py')


def lint():
    run_script('exec.py', ['lint'])


def i18n():
    run_script('localizer.py')
