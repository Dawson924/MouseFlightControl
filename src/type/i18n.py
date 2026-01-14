from typing import Any, Dict, Literal

Language = Literal['en_US', 'zn_CN', 'ru_RU']

I18n = Dict[Language, Dict[str, Any]]
