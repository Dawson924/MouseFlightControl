from typing import Any, Callable, Dict, List, NoReturn, Optional, Tuple

from type.i18n import I18nDict

ScriptOption = Tuple[str, int, Any]


class ScriptModule:
    id: str
    name: str
    options: Optional[List[ScriptOption]] = []
    i18n: Optional[I18nDict] = {}
    init: Optional[Callable[[Dict], NoReturn]] = None

    _language = 'en_US'

    def __init__(self, lang: str, **args):
        for key, value in args.items():
            setattr(self, key, value)

        self.set_language(lang)

    def translate(self, key):
        translation = self.i18n.get(key)
        if isinstance(translation, str):
            return translation
        elif isinstance(translation, dict):
            return translation.get(self._language)
        elif key == 'name' and hasattr(self, 'name'):
            return self.name
        else:
            return f'{self.id}:{key}'

    def set_language(self, lang):
        self._language = lang
        self.language_changed()

    def language_changed(self):
        self.name = self.translate('name')
