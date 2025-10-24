from PySide2.QtWidgets import QFileDialog, QMainWindow

def choose_single_file(parent: QMainWindow, caption: str, path: str, filter: str='', options: QFileDialog.Options=None):
    """选择单个文件"""
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        caption,
        path,
        filter,
        options
    )
    if file_path:
        return file_path
    else:
        return None
