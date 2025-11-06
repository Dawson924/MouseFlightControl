import glob
import os
from typing import Any, Dict, List

from lupa import LuaRuntime

from common.constants import LUA_LIBS_PATH

# 配置规则
CONFIG_RULES = {
    'attempts': (int, 1, None),
    'debug': (bool,),
    'indicator_x': (int,),
    'indicator_y': (int,),
    'indicator_bg_color': (list,),
    'indicator_line_color': (list,),
    'device': (str,),
    'device_id': (int, 1, None),
    'axis_speed': (int, 1, 20),
    'damp_x': (float, 0.1, 1),
    'damp_y': (float, 0.1, 1),
}


def load_lua_scripts(runtime: LuaRuntime, dir: str):
    lua_paths = glob.glob(os.path.join(dir, '*.lua'))
    abs_dir = os.path.abspath(dir)
    lua_globals = runtime.globals()
    lua_path = lua_globals.package.path
    lua_cpath = lua_globals.package.cpath

    # Lua 路径
    additional_paths = [
        f'{abs_dir}/?.lua',
        f'{abs_dir}/?/?.lua',
        f'{abs_dir}/?/init.lua',
        f'{LUA_LIBS_PATH}/?.lua',
        f'{LUA_LIBS_PATH}/?/?.lua',
        f'{LUA_LIBS_PATH}/?/init.lua',
    ]

    lua_globals.package.path = ';'.join(additional_paths) + ';' + lua_path

    # Lua C 路径
    additional_paths = [
        f'{LUA_LIBS_PATH}/socket/core.dll',
        f'{LUA_LIBS_PATH}/mime/core.dll',
    ]
    lua_globals.package.cpath = ';'.join(additional_paths) + ';' + lua_cpath

    script_configs: List[Dict[str, Any]] = []
    update_functions: List[Any] = []

    for path in lua_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            runtime.execute(script_content)
            globals = runtime.globals()

            # 处理Init函数（收集配置）
            init_func = globals.Init
            if init_func is not None and callable(init_func):
                lua_config = init_func()  # 调用Lua的Init，返回键值对表（或nil）
                py_config = (
                    lua_table_to_python(lua_config) if lua_config is not None else {}
                )

                # 校验配置合法性
                if isinstance(py_config, dict):
                    validate_config(py_config, path)
                    script_configs.append(py_config)

            # 处理Update函数
            update_func = globals.Update
            if update_func is not None and callable(update_func):
                update_functions.append(update_func)

        except Exception as e:
            # TODO 完善报错提示
            print(e)
            continue

    init_configs = {}
    for cfg in script_configs:
        init_configs.update(cfg)

    return init_configs, update_functions


def lua_table_to_python(lua_obj) -> Any:
    """将Lua对象转换为Python对象"""
    if hasattr(lua_obj, 'to_dict'):  # 是Lua表
        try:
            # 尝试判断是否为数组（键为连续整数1,2,3...）
            keys = list(lua_obj.keys())
            if keys == list(range(1, len(keys) + 1)):
                return [
                    lua_table_to_python(lua_obj[i]) for i in range(1, len(keys) + 1)
                ]
            else:
                # 键值对表，转换为Python字典
                return {k: lua_table_to_python(v) for k, v in lua_obj.items()}
        except:
            # 无法解析键时，默认按字典处理
            return {k: lua_table_to_python(v) for k, v in lua_obj.items()}
    else:
        # 非表类型（数字、字符串等）直接返回
        return lua_obj


def validate_config(config: Dict[str, Any], script_path: str) -> None:
    """校验配置项的合法性（键名、类型、范围）"""
    for key, value in config.items():
        if key not in CONFIG_RULES:
            raise ValueError(
                f"Invalid value: '{key}={value}' at {script_path} ({key} does not exist)"
            )

        rule = CONFIG_RULES[key]
        expected_type = None
        is_tuple = False

        if isinstance(rule, tuple):
            expected_type = rule[0]
            is_tuple = True
        elif isinstance(rule, type):
            expected_type = rule

        if not isinstance(value, expected_type):
            raise TypeError(
                f'Invalid type: {type(value).__name__} at {script_path}\n'
                f'Use {expected_type.__name__} instead'
            )

        if is_tuple and len(rule) >= 3:
            min_val, max_val = rule[1], rule[2]
            valid = True
            if min_val is not None:
                valid &= value >= min_val
            if max_val is not None:
                valid &= value <= max_val
            if not valid:
                raise ValueError(
                    f"Invalid value: '{key}={value}' at {script_path} (out of range: {min_val}~{max_val})"
                )
