import flet as ft

from src.controls import ViewContainer


class FollowView(ViewContainer):
    def __init__(self):
        super().__init__(
            icon=ft.icons.BOOKMARK_BORDER_ROUNDED,
            selected_icon=ft.icons.BOOKMARK_ROUNDED,
        )

    def build(self):
        return ft.Container(
            ft.Text("Отслеживаемые"),
            alignment=ft.alignment.center,
            expand=1,
        )
