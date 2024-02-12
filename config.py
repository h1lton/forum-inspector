import json
import os
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class Base:
    __data = None
    __file_name__: str

    @abstractmethod
    def as_dict(self) -> dict:
        pass

    def load_from_file(self) -> dict | None:
        if not os.path.exists(self.__file_name__):
            return

        with open(self.__file_name__) as f:
            data = json.load(f)
        return data

    def save_to_file(self):
        with open(self.__file_name__, "w") as f:
            json.dump(self.as_dict(), f)


class Config(Base):
    __file_name__ = "config.json"

    def __init__(self):
        self.cookie: dict | None = None
        self.last_query: str | None = None
        self.color_scheme_seed: str = "blue"
        self.theme_mode: str = "dark"

        data = self.load_from_file()
        if data:
            for key in data.keys():
                setattr(self, key, data[key])

    def as_dict(self) -> dict:
        return self.__dict__
