from typing import Any, Callable, Dict, List, NoReturn, Optional, Tuple

from type.i18n import I18n

ScriptOption = Tuple[str, str, Any]
ScriptFunction = Callable[[Any], NoReturn]


class ScriptModule:
    id: str
    name: str
    options: Optional[List[ScriptOption]] = []
    i18n: Optional[I18n]
    data: Optional[Dict[str, Any]] = None
    init: Optional[ScriptFunction] = None
    update: Optional[ScriptFunction] = None

    _language = 'en_US'

    def __init__(self, lang: str, **args):
        for key, value in args.items():
            setattr(self, key, value)

        self.set_language(lang)

    def translate(self, key):
        if not hasattr(self, 'i18n'):
            return f'{self.id}:{key}'

        locale = self.i18n.get(self._language)
        if isinstance(locale, dict):
            return locale.get(key)
        else:
            fallback = self.i18n.get('en_US')
            if isinstance(fallback, dict):
                return fallback.get(key)
            else:
                return f'{self.id}:{key}'

    def set_language(self, lang):
        self._language = lang
        self.name = self.translate('name')
