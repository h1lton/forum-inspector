from enum import StrEnum, auto
from typing import Any

import flet as ft


class Keys(StrEnum):
    last_query = auto()
    cookie = auto()


class ClientStorage:
    def __init__(self, page: ft.Page, app_name: str):
        self._page = page
        self._key_prefix = app_name + "."

    def get(self, key: Keys):
        return self._page.client_storage.get(self._key_prefix + key.name)

    def set(self, key: Keys, value: Any):
        return self._page.client_storage.set(self._key_prefix + key.name, value)

    def remove(self, key: Keys):
        return self._page.client_storage.remove(self._key_prefix + key.name)

    def get_keys(self):
        return self._page.client_storage.remove(self._key_prefix)

    def clear(self):
        for key in Keys:
            self.remove(key)
