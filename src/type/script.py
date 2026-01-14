from typing import Any, Callable, Dict, List, NoReturn, Optional, Tuple

from type.i18n import I18n

ScriptOption = Tuple[str, str, Any]


class ScriptModule:
    id: str
    name: str
    options: Optional[List[ScriptOption]] = []
    i18n: Optional[I18n]
    data: Optional[Dict[str, Any]] = None
    init: Optional[Callable[[Dict], NoReturn]] = None
    update: Optional[Callable[[float], NoReturn]] = None

    _language = 'en_US'

    def __init__(self, lang: str, **args):
        for key, value in args.items():
            setattr(self, key, value)

        self.set_language(lang)

    def translate(self, key):
        if not hasattr(self, 'i18n'):
            return f'{self.id}:{key}'

        translation = self.i18n.get(self._language)
        if isinstance(translation, dict):
            return translation.get(key)
        elif key == 'name' and hasattr(self, 'name'):
            return self.name
        else:
            return f'{self.id}:{key}'

    def set_language(self, lang):
        self._language = lang
        self.language_changed()

    def language_changed(self):
        self.name = self.translate('name')
