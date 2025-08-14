@echo off
python setup.py bdist_wheel
python ./exec.py uic
python ./exec.py lupdate
python ./exec.py lrelease
python ./pyinstaller.py
