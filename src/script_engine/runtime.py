import glob
import os
from typing import Any, List

from lupa import LuaRuntime

from common.constants import LUA_PATH
from loguru import logger
from type.script import ScriptModule


def load_lua_scripts(runtime: LuaRuntime, dir: str, language: str):
    dir = os.path.abspath(dir)
    abs_dir = os.path.abspath(dir)

    lua_paths = glob.glob(os.path.join(dir, '*.lua'))
    lua_globals = runtime.globals()
    lua_path = lua_globals.package.path
    lua_cpath = lua_globals.package.cpath

    # Lua 路径
    additional_paths = [
        f'{abs_dir}/?.lua',
        f'{abs_dir}/?/?.lua',
        f'{abs_dir}/?/init.lua',
        f'{LUA_PATH}/?.lua',
        f'{LUA_PATH}/?/?.lua',
        f'{LUA_PATH}/?/init.lua',
    ]

    lua_globals.package.path = ';'.join(additional_paths) + ';' + lua_path

    # Lua C 路径
    additional_paths = [
        f'{LUA_PATH}/socket/core.dll',
        f'{LUA_PATH}/mime/core.dll',
    ]
    lua_globals.package.cpath = ';'.join(additional_paths) + ';' + lua_cpath

    scripts: List[ScriptModule] = []
    for path in lua_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            result = runtime.execute(script_content)
            if result is not None:
                object = lua_table_to_python(result)
                script = ScriptModule(language, **object)
                scripts.append(script)

        except Exception as e:
            logger.exception(e)
            continue

    return scripts


def lua_table_to_python(lua_obj) -> Any:
    if hasattr(lua_obj, 'to_dict'):
        try:
            keys = list(lua_obj.keys())
            if keys == list(range(1, len(keys) + 1)):
                return [lua_table_to_python(lua_obj[i]) for i in range(1, len(keys) + 1)]
            else:
                return {k: lua_table_to_python(v) for k, v in lua_obj.items()}
        except:
            return {k: lua_table_to_python(v) for k, v in lua_obj.items()}
    else:
        return lua_obj
