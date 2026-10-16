import os
from typing import Any, Dict, List, Optional

from loguru import logger

from .runtime import Extension, RuntimeContext

ALLOWED_IMPORTS = {
    'typing',
    'datetime',
    'os',
    'pathlib',
    'json',
    'math',
    'collections',
    'functools',
    'itertools',
    'abc',
    'dataclasses',
    'enum',
    'copy',
    're',
    'time',
    'threading',
    'queue',
    'loguru',
    'PySide2.QtCore',
    'PySide2.QtWidgets',
    'PySide2.QtGui',
    'plugin.runtime',
    'plugin.config',
    'plugin.mixin',
    'win32',
    'axis',
}


LIB_MODULE_NAMES = {'win32', 'axis', 'data'}


class ExtensionLoader:
    def __init__(self):
        self._all: Dict[str, Extension] = {}
        self._contexts: Dict[str, RuntimeContext] = {}
        self._extensions: List[Extension] = []
        self._current_model: Optional[str] = None
        self._current_ext: Optional[Extension] = None

    @property
    def extensions(self) -> List[Extension]:
        return self._extensions

    @property
    def current(self) -> Optional[Extension]:
        return self._current_ext

    @property
    def current_model(self) -> Optional[str]:
        return self._current_model

    @property
    def current_context(self) -> Optional[RuntimeContext]:
        if self._current_model:
            return self._contexts.get(self._current_model)
        return None

    def load_extension(self, file_path: str, ext_id: str) -> Optional[Extension]:
        try:
            ext = self._load_from_file(file_path, ext_id)

            if not ext:
                return None

            self._extensions.append(ext)
            self._all[ext_id] = ext
            runtime = RuntimeContext()
            self._contexts[ext_id] = runtime
            ext.setup(runtime)

            logger.info(f'Loaded extension: {ext.id} from {file_path}')
            return ext

        except Exception as e:
            logger.exception(f'Failed to load extension from {file_path}: {e}')
            return None

    def load(self, extensions_dir: str) -> int:
        if not os.path.isdir(extensions_dir):
            logger.warning(f'Extensions directory does not exist: {extensions_dir}')
            return 0

        loaded_count = 0

        for item in os.listdir(extensions_dir):
            ext_path = os.path.join(extensions_dir, item)

            if os.path.isdir(ext_path):
                entry_files = ['extension.py', 'main.py']
                loaded = False
                for entry_file in entry_files:
                    full_path = os.path.join(ext_path, entry_file)
                    if os.path.isfile(full_path):
                        ext_id = item
                        if self.load_extension(full_path, ext_id):
                            loaded_count += 1
                            loaded = True
                        break

                if not loaded:
                    for py_file in os.listdir(ext_path):
                        if py_file.endswith('.py') and not py_file.startswith('_'):
                            full_path = os.path.join(ext_path, py_file)
                            ext_id = os.path.splitext(py_file)[0]
                            if self.load_extension(full_path, ext_id):
                                loaded_count += 1
                                break

            elif item.endswith('.py') and not item.startswith('_'):
                ext_name = os.path.splitext(item)[0]
                ext_id = ext_name
                if self.load_extension(ext_path, ext_id):
                    loaded_count += 1

        logger.info(f'Loaded {loaded_count} extensions from {extensions_dir}')
        return loaded_count

    def load_model(self, module_path: str, model: str) -> Optional[Extension]:
        main_py = os.path.join(module_path, 'main.py')

        if not os.path.isfile(main_py):
            return None

        ext = self.load_extension(main_py, model)

        if ext:
            self._current_model = model
            self._current_ext = ext
            logger.info(f'Switched to model extension: {ext.id} for {model}')

        return ext

    def _restricted_import(self, name: str, globals=None, locals=None, fromlist=(), level=0):
        if name in LIB_MODULE_NAMES:
            name = f'lib.{name}'
        elif name not in ALLOWED_IMPORTS and not any(name.startswith(allowed + '.') for allowed in ALLOWED_IMPORTS):
            raise ImportError(f"Import '{name}' is not allowed in plugin environment")
        if '.' in name:
            parts = name.split('.')
            mod = __import__(parts[0])
            for part in parts[1:]:
                mod = getattr(mod, part)
            return mod
        return __import__(name, globals, locals, fromlist, level)

    def _create_env(self, ext_id: str) -> Dict[str, Any]:
        original_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__

        safe_builtins = {
            '__import__': self._restricted_import,
            '__build_class__': original_builtins.get('__build_class__'),
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'frozenset': frozenset,
            'None': None,
            'True': True,
            'False': False,
            'type': type,
            'isinstance': isinstance,
            'issubclass': issubclass,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'delattr': delattr,
            'callable': callable,
            'sorted': sorted,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'any': any,
            'all': all,
            'open': open,
            'compile': compile,
            'eval': eval,
            'exec': exec,
            'format': format,
            'hash': hash,
            'id': id,
            'iter': iter,
            'next': next,
            'ord': ord,
            'chr': chr,
            'bin': bin,
            'hex': hex,
            'oct': oct,
            'pow': pow,
            'repr': repr,
            'slice': slice,
            'staticmethod': staticmethod,
            'classmethod': classmethod,
            'property': property,
            'super': super,
            'object': object,
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'AttributeError': AttributeError,
            'RuntimeError': RuntimeError,
            'StopIteration': StopIteration,
            'GeneratorExit': GeneratorExit,
            'AssertionError': AssertionError,
            'ImportError': ImportError,
            'ModuleNotFoundError': ModuleNotFoundError,
            'NotImplementedError': NotImplementedError,
            'ZeroDivisionError': ZeroDivisionError,
            'OverflowError': OverflowError,
            'FloatingPointError': FloatingPointError,
            'OSError': OSError,
            'IOError': IOError,
            'FileNotFoundError': FileNotFoundError,
            'PermissionError': PermissionError,
        }

        env = {
            '__name__': f'ext_{ext_id}',
            '__file__': '',
            '__builtins__': safe_builtins,
            '__doc__': None,
        }

        for module_name in ALLOWED_IMPORTS:
            try:
                if module_name in LIB_MODULE_NAMES:
                    continue
                elif '.' in module_name:
                    parts = module_name.split('.')
                    parent_module = __import__(parts[0])
                    for part in parts[1:]:
                        parent_module = getattr(parent_module, part)
                    env[module_name] = parent_module
                else:
                    env[module_name] = __import__(module_name)
            except ImportError:
                pass

        return env

    def _load_from_file(self, file_path: str, module_name: str) -> Optional[Extension]:
        env = self._create_env(module_name)
        env['__file__'] = file_path

        from .mixin import get_global_registry

        initial_replace_keys = set(get_global_registry()._replace.keys())
        initial_add_keys = set(get_global_registry()._add.keys())
        initial_wrap_keys = set(get_global_registry()._wrap.keys())

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        try:
            exec(code, env)
        except Exception as e:
            logger.exception(f'Failed to execute plugin code: {e}')
            raise

        plugin_replace_keys = set(get_global_registry()._replace.keys()) - initial_replace_keys
        plugin_add_keys = set(get_global_registry()._add.keys()) - initial_add_keys
        plugin_wrap_keys = set(get_global_registry()._wrap.keys()) - initial_wrap_keys

        ext_class = env.get('Plugin', None)

        if ext_class is None:
            plugin_classes = [
                obj
                for name, obj in env.items()
                if isinstance(obj, type) and issubclass(obj, Extension) and obj is not Extension
            ]

            if len(plugin_classes) == 1:
                ext_class = plugin_classes[0]
            elif len(plugin_classes) > 1:
                for cls in plugin_classes:
                    try:
                        instance = cls()
                        instance_ext_id = f'{cls.__name__.lower()}'

                        self._extensions.append(instance)
                        self._all[instance_ext_id] = instance
                        runtime = RuntimeContext()
                        runtime._env = env
                        self._contexts[instance_ext_id] = runtime
                        instance.setup(runtime)

                        logger.info(f'Loaded extension: {instance.id} ({cls.__name__}) from {file_path}')
                    except Exception as e:
                        logger.exception(f'Failed to initialize {cls.__name__}: {e}')

                return None

        if ext_class is None:
            logger.warning(f'No Plugin class found in {file_path}')
            return None

        if not (isinstance(ext_class, type) and issubclass(ext_class, Extension)):
            logger.warning(f'Plugin class in {file_path} is not a valid Extension subclass')
            return None

        instance = ext_class()
        runtime = RuntimeContext()
        runtime._env = env

        from .mixin import MixinRegistry, apply_mixins, get_global_registry

        plugin_mixins = MixinRegistry()
        for key in plugin_replace_keys:
            plugin_mixins._replace[key] = get_global_registry()._replace[key]
        for key in plugin_add_keys:
            plugin_mixins._add[key] = get_global_registry()._add[key]
        for key in plugin_wrap_keys:
            if key not in plugin_mixins._wrap:
                plugin_mixins._wrap[key] = []
            plugin_mixins._wrap[key].append(get_global_registry()._wrap[key][-1])

        from plugin.mixin import _try_import_class

        all_targets = list(plugin_replace_keys) + list(plugin_add_keys) + list(plugin_wrap_keys)
        for target in all_targets:
            class_path = target.rsplit('.', 1)[0]
            _try_import_class(class_path)

        apply_mixins(plugin_mixins)

        return instance

    def get(self, ext_id: str) -> Optional[Extension]:
        return self._all.get(ext_id)

    def get_context(self, ext_id: str) -> Optional[RuntimeContext]:
        return self._contexts.get(ext_id)

    def unload(self, ext_id: str) -> bool:
        ext = self._all.pop(ext_id, None)

        if ext is None:
            return False

        try:
            ext.teardown()
        except Exception as e:
            logger.exception(f'Error during teardown for {ext_id}: {e}')

        self._contexts.pop(ext_id, None)

        if ext in self._extensions:
            self._extensions.remove(ext)

        if ext_id == self._current_model:
            self._current_model = None
            self._current_ext = None

        logger.info(f'Unloaded extension: {ext_id}')
        return True

    def on_model_changed(self, model: str, modules: Dict[str, Any]) -> None:
        if model == self._current_model:
            return

        if self._current_model:
            self.unload(self._current_model)

        self._current_model = model

        if model in modules:
            module_info = modules[model]
            module_path = module_info.get('module_path')

            if module_path:
                ext = self.load_model(module_path, model)
                if ext:
                    logger.info(f'Model extension active: {ext.id} for {model}')

    def tick(self, dt: float) -> None:
        for ext in self._extensions:
            try:
                ext.tick(dt)
            except Exception as e:
                logger.error(f'Extension tick error ({ext.id}): {e}')

    def start_all(self) -> None:
        for ext in self._extensions:
            try:
                ext.start()
            except Exception as e:
                logger.error(f'Failed to start extension {ext.id}: {e}')

    def stop_all(self) -> None:
        for ext in self._extensions:
            try:
                ext.stop()
            except Exception as e:
                logger.error(f'Failed to stop extension {ext.id}: {e}')

    def emit_event(self, event_name: str, *args, **kwargs) -> List[Any]:
        results = []

        for ext_id, runtime in self._contexts.items():
            result = runtime.emit(event_name, *args, **kwargs)
            results.extend(result)

        return results


extension_loader = ExtensionLoader()

__all__ = [
    'ExtensionLoader',
    'extension_loader',
]