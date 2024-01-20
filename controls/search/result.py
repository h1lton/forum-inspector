import flet as ft


class Prefix(ft.Container):
    def __init__(self, name: str):
        super().__init__()

        text = ft.Text(value=name, size=10, weight=ft.FontWeight.W_600)

        self.content = text
        self.border_radius = 6
        self.padding = 5

        if name == "ОДОБРЕНО":
            self.bgcolor = ft.colors.GREEN_ACCENT_700
            text.color = ft.colors.WHITE70
        elif name == "ОТКАЗАНО":
            self.bgcolor = ft.colors.RED_ACCENT_700
            text.color = ft.colors.WHITE70
        else:
            self.bgcolor = ft.colors.LIGHT_BLUE_ACCENT_700
            text.color = ft.colors.BLACK87


class Result(ft.Container):
    def __init__(
        self,
        index: int,
        prefix: str,
        user: str,
        date: str,
        chapter: str,
        link: str,
    ):
        super().__init__()

        self.expand = 1
        self.border_radius = 10
        # self.bgcolor = ft.colors.BLACK45
        self.padding = 10

        title = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(value=f"{index}. {date}"),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        if prefix:
            title.controls.append(Prefix(prefix))

        content = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(value=user),
                        ft.Text(value=chapter),
                    ],
                    spacing=2,
                ),
            ],
        )

        self.content = ft.Column(
            controls=[
                title,
                content,
            ],
            spacing=3,
        )

        self.on_hover = self.hover_event

        self.on_click = lambda e: self.page.launch_url(link)

    def hover_event(self, e):
        self.bgcolor = ft.colors.OUTLINE_VARIANT if e.data == "true" else None
        self.update()
