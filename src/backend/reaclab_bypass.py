import dataclasses
import re
import time
from datetime import timedelta

from Crypto.Cipher import AES
from aiohttp import ClientSession

from src.config import Config


class ReactLabBypassException(Exception):
    pass


@dataclasses.dataclass
class ReactLabBypass:
    """
    Обход защиты React Lab

    :param site Сайт на котором защита
    :param cookie_expires_at конечный срок действия cookie
    """

    config: Config
    session: ClientSession
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

    def set_cookie_in_storage(self, value: dict):
        self.config.cookie = value

    def _set_cookie(self):
        """Устанавливает имеющиеся куки в сессию"""
        self.session.cookie_jar.update_cookies(
            {self.cookie_name: self.cookie_value}, self.session._base_url
        )

    async def _get_cookie(self) -> None:
        """
        Запрашивает и расшифровывает данные на странице сохраняя их в конфиг и класс.
        """
        response = await self.session.get("/")
        line = (await response.text()).splitlines()[-8]
        line = re.sub(r"\\x([A-F0-9]{2})", lambda m: chr(int(m.group(1), 16)), line)

        keys = re.findall(r"[a-f0-9]{32}", line)

        if not keys:
            raise ReactLabBypassException("cannot get keys")

        self.cookie_name = re.search(r'","cookie","(?P<name>[^=]+)', line).group("name")

        key = bytes.fromhex(keys[0])
        iv = bytes.fromhex(keys[1])
        cipher = bytes.fromhex(keys[2])

        self.cookie_value = bytes.hex(AES.new(key, AES.MODE_CBC, iv=iv).decrypt(cipher))
        self.cookie_expires_at = time.time() + timedelta(days=365).total_seconds()
        self.config.cookie = {
            "name": self.cookie_name,
            "value": self.cookie_value,
            "expires": self.cookie_expires_at,
        }

    async def set_cookie(self) -> None:
        """
        Устанавливает имеющиеся куки в сессию если они валидны, если нет запрашивает новые.
        """

        if not self.is_cookie_valid:
            if self.config.cookie:
                self.cookie_name = self.config.cookie["name"]
                self.cookie_value = self.config.cookie["value"]
                self.cookie_expires_at = self.config.cookie["expires"]
                if not self.is_cookie_valid:
                    await self._get_cookie()
            else:
                await self._get_cookie()

        self._set_cookie()
