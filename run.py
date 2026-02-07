import importlib.util
import os
import subprocess
import sys
from typing import List

PROJECT_ROOT = os.getcwd()
sys.path.insert(0, PROJECT_ROOT)
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
sys.path.insert(0, SRC_DIR)


def run_python_script(script_path: str, args: List[str] = None):
    args = args or []

    abs_script_path = os.path.abspath(script_path)
    if not os.path.exists(abs_script_path):
        raise FileNotFoundError(f'Python script file does not exist: {abs_script_path}')

    original_argv = sys.argv.copy()
    try:
        sys.argv = [abs_script_path] + args

        spec = importlib.util.spec_from_file_location('__main__', abs_script_path)
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)
    finally:
        sys.argv = original_argv


def run_command(command: List[str], cwd: str = None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd or PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f'Command execution failed: {e}')
        print(f'Error output: {e.stderr}')
        raise


def dev():
    run_command(
        ['pyside2-uic', './src/ui/MainWindow.ui', '-o', './src/ui/MainWindow.py']
    )
    run_python_script(os.path.join('src', 'main.py'))


def build():
    run_command(
        ['pyside2-uic', './src/ui/MainWindow.ui', '-o', './src/ui/MainWindow.py']
    )
    run_python_script('pyinstaller.py')


def lint():
    run_command(['ruff', 'format', '.'])
    run_command(['ruff', 'check', '--fix', '.'])


def i18n():
    run_python_script('localizer.py')
