@echo off
python ./exec.py uic
python ./exec.py lupdate
python ./exec.py lrelease
python ./src/main.py
