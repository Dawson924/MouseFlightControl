from typing import Dict, TypedDict


class LanguageMap(TypedDict):
    en_US: str
    zh_CN: str


I18nDict = Dict[str, LanguageMap]
