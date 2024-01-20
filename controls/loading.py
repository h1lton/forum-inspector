import flet as ft


class Loading(ft.UserControl):
    def __init__(self, status: str = "Загрузка"):
        super().__init__()
        self.status = status

    def build(self):
        self.status_field = ft.Text(self.status)
        return ft.Column(
            [
                self.status_field,
                ft.Image("loading.gif", height=391 / 5, width=498 / 5),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def update_status(self, message):
        self.status_field.value = message
        self.update()
