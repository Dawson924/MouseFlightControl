import os
import subprocess
from typing import List

python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')

if not os.path.exists(python):
    raise FileNotFoundError(python)

def run(cmds: List[str]):
    subprocess.run(cmds, check=True)


def dev():
    run([python, 'exec.py', 'uic'])
    run([python, 'src/main.py'])


def build():
    run([python, 'exec.py', 'uic'])
    run([python, 'pyinstaller.py'])
