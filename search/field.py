import flet as ft


class SearchField(ft.Container):
    def __init__(self, value: str, on_submit):
        super().__init__()

        self.bgcolor = ft.colors.BACKGROUND
        self.border_radius = 15
        self.margin = ft.Margin(top=11, left=11, right=11, bottom=0)
        self.shadow = ft.BoxShadow(blur_radius=5)

        self.field = ft.TextField(
            value=value,
            on_submit=on_submit,
            hint_text="Что ищем?",
            expand=1,
            border=ft.InputBorder.NONE,
            prefix_icon=ft.icons.SEARCH,
            color=ft.colors.BLACK,
            hint_style=ft.TextStyle(
                color=ft.colors.BLACK54,
                # weight=ft.FontWeight.NORMAL,
            ),
        )

        # self.btn = ft.FloatingActionButton(
        #     icon=ft.icons.SEARCH,
        #     on_click=on_submit,
        #     mini=True,
        # )
        # self.padding = ft.Padding(left=0, right=4, top=0, bottom=0)

        self.content = ft.Row(
            controls=[
                self.field,
                # self.btn,
            ],
            spacing=0,
        )

        color_scheme = ft.ColorScheme(
            background=ft.colors.BLUE_GREY_200,
            on_surface_variant=ft.colors.BLACK54,  # prefix_icon
        )

        self.theme = ft.Theme(color_scheme=color_scheme)

    @property
    def value(self) -> str | None:
        return self.field.value

    @value.setter
    def value(self, value: str | None):
        self.field.value = value
