import glob
import os
from typing import Any, Dict, List

from lupa import LuaRuntime

# 配置规则
CONFIG_RULES = {
    'indicator_x': (int, 30),  # 包含类型、默认值、最小值、最大值
    'indicator_y': (int, -30),
}

# 从规则中提取默认配置（自动生成DEFAULT_CONFIG）
DEFAULT_CONFIG = {key: rule[1] for key, rule in CONFIG_RULES.items()}


def load_lua_scripts(runtime: LuaRuntime, dir: str):
    if not os.path.isdir(dir):
        return DEFAULT_CONFIG.copy(), []

    lua_paths = glob.glob(os.path.join(dir, '*.lua'))
    abs_dir = os.path.abspath(dir)
    additional_paths = [
        f'{abs_dir}/?.lua',
        f'{abs_dir}/?/?.lua',
        f'{abs_dir}/?/init.lua',
    ]
    lua_globals = runtime.globals()
    current_path = lua_globals.package.path
    lua_globals.package.path = ';'.join(additional_paths) + ';' + current_path

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
                else:
                    print(f'脚本 {path} 的Init返回非表类型，已忽略')

            # 处理Update函数
            update_func = globals.Update
            if update_func is not None and callable(update_func):
                update_functions.append(update_func)

        except Exception as e:
            print(f'加载脚本 {path} 失败：{str(e)}')
            continue

    # 合并所有脚本配置和默认配置
    merged_config = DEFAULT_CONFIG.copy()
    for cfg in script_configs:
        merged_config.update(cfg)

    return merged_config, update_functions


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
            valid_keys = list(CONFIG_RULES.keys())
            raise ValueError(
                f'脚本 {script_path} 包含无效配置项：{key}（合法项：{valid_keys}）'
            )

        # 解析规则：(类型, 默认值, [最小值, 最大值])
        rule = CONFIG_RULES[key]
        expected_type = rule[0]

        # 校验类型
        if not isinstance(value, expected_type):
            raise TypeError(
                f'脚本 {script_path} 配置 {key} 类型错误：'
                f'期望 {expected_type.__name__}，实际 {type(value).__name__}'
            )

        # 校验范围（如果规则中包含范围参数）
        if len(rule) >= 4:  # 存在最小值和最大值（规则长度为4）
            min_val, max_val = rule[2], rule[3]
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f'脚本 {script_path} 配置 {key} 超出范围：'
                    f'[{min_val}, {max_val}]，实际 {value}'
                )
