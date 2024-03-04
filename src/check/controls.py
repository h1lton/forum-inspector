import flet as ft

from src.controls import ViewContainer


class CheckView(ViewContainer):
    def __init__(self):
        super().__init__(
            icon=ft.icons.ACCESS_TIME_ROUNDED,
            selected_icon=ft.icons.ACCESS_TIME_FILLED_ROUNDED,
        )

    def build(self):
        return ft.Container(
            ft.Text("Отложенные"),
            alignment=ft.alignment.center,
            expand=1,
        )
