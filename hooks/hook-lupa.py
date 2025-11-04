from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs(package='lupa', search_patterns=['*.pyd'])

hiddenimports = ['lupa._lupa']
