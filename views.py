from dataclasses import dataclass

from flet_core import Control


@dataclass
class View:
    name: str
    view: Control
    icon: str
    selected_icon: str | None = None
