from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs(
    package='pyvjoy', destdir='.', search_patterns=['*.dll']
)
hiddenimports = []
