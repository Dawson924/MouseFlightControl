import os
from typing import Optional

from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices
from PySide2.QtWidgets import QFileDialog, QMainWindow


def choose_single_file(
    parent: QMainWindow,
    caption: str,
    path: str,
    filter: str = '',
    options: QFileDialog.Options = None,
):
    file_path, _ = QFileDialog.getOpenFileName(parent, caption, path, filter, options)
    return file_path if file_path else None


def choose_multiple_files(
    parent: QMainWindow,
    caption: str,
    path: str,
    filter: str = '',
    options: QFileDialog.Options = None,
):
    files, _ = QFileDialog.getOpenFileNames(
        parent, caption, path, filter, options or QFileDialog.Options()
    )
    return files if files else []


def choose_directory(
    parent: QMainWindow,
    caption: str,
    path: str,
    options: QFileDialog.Options = None,
):
    dir_path = QFileDialog.getExistingDirectory(
        parent, caption, path, options or QFileDialog.Options()
    )
    return dir_path if dir_path else None


def ensure(path: str, content: str = None) -> None:
    if os.path.splitext(path)[1]:
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        if not os.path.exists(path):
            with open(path, 'a') as f:
                f.write(content)
    else:
        os.makedirs(path, exist_ok=True)


def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    if not os.path.exists(file_path):
        print(f'Path not exists: {file_path}')
        return None

    if not os.path.isfile(file_path):
        print(f'File not found: {file_path}')
        return None

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except PermissionError:
        print(f'Permission denied: {file_path}')
    except UnicodeDecodeError as e:
        print(str(e))
    except Exception as e:
        print(str(e))

    return None


def save_file(
    parent: QMainWindow,
    caption: str,
    path: str,
    filter: str = '',
    options: QFileDialog.Options = None,
):
    file_path, _ = QFileDialog.getSaveFileName(
        parent, caption, path, filter, options or QFileDialog.Options()
    )
    return file_path if file_path else None


def open_file(file_path: str) -> bool:
    return QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))


def open_directory(dir_path: str) -> bool:
    return QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))
