import importlib
import sys
from typing import Callable, Dict, List, Optional

from loguru import logger


class MixinRegistry:
    def __init__(self):
        self._replace: Dict[str, Callable] = {}
        self._add: Dict[str, Callable] = {}
        self._wrap: Dict[str, Callable] = {}

    def register_replace(self, target: str, func: Callable) -> None:
        self._replace[target] = func

    def register_add(self, target: str, func: Callable) -> None:
        self._add[target] = func

    def register_wrap(self, target: str, func: Callable) -> None:
        if target not in self._wrap:
            self._wrap[target] = []
        self._wrap[target].append(func)

    def get_replace(self, target: str) -> Optional[Callable]:
        return self._replace.get(target)

    def get_add(self, target: str) -> Optional[Callable]:
        return self._add.get(target)

    def get_wraps(self, target: str) -> List[Callable]:
        return self._wrap.get(target, [])

    def clear(self) -> None:
        self._replace.clear()
        self._add.clear()
        self._wrap.clear()


_global_registry = MixinRegistry()


def replace(target: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        _global_registry.register_replace(target, func)
        return func

    return decorator


def add(target: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        _global_registry.register_add(target, func)
        return func

    return decorator


def wrap(target: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        _global_registry.register_wrap(target, func)
        return func

    return decorator


def get_global_registry() -> MixinRegistry:
    return _global_registry


def clear_global_registry() -> None:
    _global_registry.clear()


def resolve_target(target: str) -> tuple:
    parts = target.rsplit('.', 1)
    if len(parts) == 2:
        class_path, method_name = parts
    elif len(parts) == 1 and parts[0]:
        class_path = parts[0]
        method_name = None
    else:
        raise ValueError(f"Invalid target format: {target}. Expected 'Class.method' or 'Class'")
    return class_path, method_name


def resolve_target_with_funcname(target: str, func: Callable) -> tuple:
    class_path, method_name = resolve_target(target)
    if method_name is None:
        method_name = func.__name__
    return class_path, method_name


def apply_mixins(registry: MixinRegistry, base_classes: List[type] = None) -> None:
    base_classes = base_classes or []
    for target, func in registry._replace.items():
        _apply_replace(target, func, base_classes)

    for target, func in registry._add.items():
        _apply_add(target, func, base_classes)

    for target, funcs in registry._wrap.items():
        for func in funcs:
            _apply_wrap(target, func, base_classes)


def _try_import_class(class_path: str) -> Optional[type]:
    if '.' not in class_path:
        return None

    module_path, class_name = class_path.rsplit('.', 1)
    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name, None)
        if cls is not None and isinstance(cls, type):
            return cls
    except (ImportError, AttributeError):
        pass
    return None


def _search_class_by_name(class_name: str) -> Optional[type]:
    for name, module in list(sys.modules.items()):
        if module is None:
            continue
        try:
            cls = getattr(module, class_name, None)
            if cls is not None and isinstance(cls, type):
                return cls
        except Exception:
            continue
    return None


def _search_class_in_hierarchy(class_name: str, base_classes: List[type]) -> Optional[type]:
    for base in base_classes:
        if base.__name__ == class_name:
            return base

        for attr_name in dir(base):
            try:
                attr = getattr(base, attr_name)
                if isinstance(attr, type) and attr.__name__ == class_name:
                    return attr
            except Exception:
                continue

        for attr_name in base.__dict__:
            attr = base.__dict__[attr_name]
            if isinstance(attr, type) and attr.__name__ == class_name:
                return attr

    return None


def _resolve_class(class_path: str, base_classes: List[type]) -> Optional[type]:
    cls = _search_class_in_hierarchy(class_path, base_classes)
    if cls:
        return cls

    if '.' in class_path:
        cls = _try_import_class(class_path)
        if cls:
            return cls

    class_name = class_path.rsplit('.', 1)[-1]
    return _search_class_by_name(class_name)


def _apply_replace(target: str, func: Callable, base_classes: List[type]) -> None:
    try:
        class_path, method_name = resolve_target_with_funcname(target, func)
        target_class = _resolve_class(class_path, base_classes)
        if target_class:
            setattr(target_class, method_name, func)
            logger.info(f'Mixin: Replaced {class_path}.{method_name}')
        else:
            logger.warning(f'Mixin: Could not find class for {class_path}')
    except Exception as e:
        logger.warning(f'Mixin replace failed for {target}: {e}')


def _apply_add(target: str, func: Callable, base_classes: List[type]) -> None:
    try:
        class_path, method_name = resolve_target_with_funcname(target, func)
        target_class = _resolve_class(class_path, base_classes)
        if target_class and not hasattr(target_class, method_name):
            setattr(target_class, method_name, func)
            logger.info(f'Mixin: Added {class_path}.{method_name}')
        elif target_class is None:
            logger.warning(f'Mixin: Could not find class for {class_path}')
    except Exception as e:
        logger.warning(f'Mixin add failed for {target}: {e}')


def _apply_wrap(target: str, func: Callable, base_classes: List[type]) -> None:
    try:
        class_path, method_name = resolve_target_with_funcname(target, func)
        target_class = _resolve_class(class_path, base_classes)
        if target_class and hasattr(target_class, method_name):
            original_method = getattr(target_class, method_name)
            wrapper = _create_wrapper(func, original_method)
            setattr(target_class, method_name, wrapper)
            logger.info(f'Mixin: Wrapped {class_path}.{method_name}')
        elif target_class is None:
            logger.warning(f'Mixin: Could not find class for {class_path}')
    except Exception as e:
        logger.warning(f'Mixin wrap failed for {target}: {e}')


def _create_wrapper(wrap_func: Callable, original: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return wrap_func(original, *args, **kwargs)

    return wrapper