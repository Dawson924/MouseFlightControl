import os

import lupa
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

lupa_dir = os.path.dirname(lupa.__file__)

datas = collect_data_files(
    package='lupa',
)

# 2. 收集动态库（.pyd、.dll等）
binaries = collect_dynamic_libs(package='lupa', search_patterns=['*.pyd'])

# 3. 显式声明隐藏依赖（lupa动态导入的子模块）
hiddenimports = [
    'lupa._lupa',  # 核心底层模块
]
