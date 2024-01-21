import dataclasses
import re
import time
import requests

from datetime import timedelta
from Crypto.Cipher import AES

from client_storage import ClientStorage, Keys


class ReactLabBypassException(Exception):
    pass


@dataclasses.dataclass
class ReactLabBypass:
    """
    Обход защиты React Lab

    :param site Сайт на котором защита
    :param cookie_expires_at конечный срок действия cookie
    """

    site: str
    client_storage: ClientStorage
    cookie_expires_at: float = 0
    cookie_name: str | None = None
    cookie_value: str | None = None

    @property
    def is_cookie_expired(self) -> bool:
        """Проверка закончился ли срок действия cookie."""
        return self.cookie_expires_at - time.time() < 0

    @property
    def is_cookie_valid(self) -> bool:
        """Проверка валидности cookie"""
        return self.cookie_name and self.cookie_value and not self.is_cookie_expired

    def get_cookie_from_storage(self):
        return self.client_storage.get(Keys.cookie)

    def set_cookie_in_storage(self, value: dict):
        self.client_storage.set(Keys.cookie, value)

    def __get_cookie(self, html) -> dict[str]:
        """
        Расшифровывает данные на странице сохраняя и возвращая cookie в виде словаря
        """
        line = html.splitlines()[-8]
        line = re.sub(r"\\x([A-F0-9]{2})", lambda m: chr(int(m.group(1), 16)), line)

        keys = re.findall(r"[a-f0-9]{32}", line)

        if not keys:
            raise ReactLabBypassException("cannot get keys")

        self.cookie_name = re.search(r'","cookie","(?P<name>[^=]+)', line).group("name")

        key = bytes.fromhex(keys[0])
        iv = bytes.fromhex(keys[1])
        cipher = bytes.fromhex(keys[2])

        self.cookie_value = bytes.hex(AES.new(key, AES.MODE_CBC, iv=iv).decrypt(cipher))
        self.cookie_expires_at = time.time() + timedelta(days=399).total_seconds()
        self.set_cookie_in_storage(
            {
                "name": self.cookie_name,
                "value": self.cookie_value,
                "expires": self.cookie_expires_at,
            }
        )
        return {self.cookie_name: self.cookie_value}

    def get_cookie(self) -> dict[str]:
        """
        Возвращает cookie в виде словаря
        Если cookie были получены ранее проверяет их на валидность,
        если валидны, то возвращает их, если нет, то запрашивает новые
        """
        if self.is_cookie_valid:
            return {self.cookie_name: self.cookie_value}

        cookie_in_storage = self.get_cookie_from_storage()

        if cookie_in_storage:
            self.cookie_name = cookie_in_storage["name"]
            self.cookie_value = cookie_in_storage["value"]
            self.cookie_expires_at = cookie_in_storage["expires"]

        if self.is_cookie_valid:
            return {self.cookie_name: self.cookie_value}

        response = requests.get(self.site)
        return self.__get_cookie(response.text)
