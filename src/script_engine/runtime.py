import glob
import os
from lupa import LuaRuntime

def load_lua_scripts(runtime: LuaRuntime, dir: str):
    if not os.path.isdir(dir):
        return [], []

    lua_paths = glob.glob(os.path.join(dir, "*.lua"))
    abs_dir = os.path.abspath(dir)
    additional_paths = [
        f"{abs_dir}/?.lua",
        f"{abs_dir}/?/?.lua",
        f"{abs_dir}/?/init.lua"
    ]
    lua_globals = runtime.globals()
    current_path = lua_globals.package.path
    lua_globals.package.path = ";".join(additional_paths) + ";" + current_path

    lua_inits = []
    lua_funcs = []
    for path in lua_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                script_content = f.read()

            runtime.execute(script_content)

            init_func = runtime.globals().init
            if not callable(init_func):
                raise RuntimeError(f'Missing "init" function at {path}: \n{script_content}')

            python_result = []
            for item in init_func().items():
                value = lua_table_to_python(item[1])
                python_result.append(value)

            lua_inits.extend(python_result)
            update_func = runtime.globals().update
            if not callable(update_func):
                raise RuntimeError(f'Missing "update" function at {path}: \n{script_content}')
            lua_funcs.append(update_func)
        except Exception as e:
            # TODO 打印错误日志
            print(e)
            continue

    return lua_inits, lua_funcs

def lua_table_to_python(lua_obj):
    if hasattr(lua_obj, 'to_dict'):
        is_array = True
        try:
            keys = list(lua_obj.keys())
            if keys != list(range(1, len(keys)+1)):
                is_array = False
        except:
            is_array = False

        if is_array:
            return [lua_table_to_python(lua_obj[i]) for i in range(1, len(keys)+1)]
        else:
            return {k: lua_table_to_python(v) for k, v in lua_obj.items()}
    else:
        return lua_obj
