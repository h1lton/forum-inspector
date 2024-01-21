import atexit

import flet as ft

from client_storage import ClientStorage
from search.view import SearchView


class App:
    def __init__(self):
        self.client_storage: ClientStorage | None = None
        self.page: ft.Page | None = None

    def start_up(self, page: ft.Page):
        self.page = page

        page.title = "Forum Inspector"
        page.window_width = page.window_min_width = 550
        page.window_height = page.window_min_height = 800
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.padding = 0
        page.spacing = 0
        page.window_center()

        self.client_storage = ClientStorage(page, page.title)

        self.loading_app()

    def loading_app(self):
        """Загружает приложение."""

        self.search_view = SearchView(self.client_storage)
        self.page.add(self.search_view)

    def destroy(self):
        print("destroy")


if __name__ == "__main__":
    app = App()
    atexit.register(app.destroy)
    ft.app(target=app.start_up, view=ft.FLET_APP_HIDDEN)
