import flet as ft

from client_storage import ClientStorage, Keys
from controls.loading import Loading
from .field import SearchField
from .result import Result
from search_driver import SearchDriver


class SearchView(ft.UserControl):
    def __init__(self, driver: SearchDriver, client_storage: ClientStorage):
        super().__init__()
        self.driver = driver
        self.client_storage = client_storage
        self.last_query = self.client_storage.get(Keys.last_query)

    def build(self):
        self.expand = 1
        self.width = 550

        self.field = SearchField(self.last_query, self.search)

        self.results = ft.ListView(
            expand=1,
            spacing=0,
            padding=20,
        )

        self.loading = Loading("Поиск...")
        self.loading.visible = False

        self.column = ft.Stack(
            [
                self.loading,
                self.results,
            ],
            expand=1,
        )

        return [
            ft.Column(
                [
                    self.field,
                    self.column,
                ],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # ft.FloatingActionButton(
            #     icon=ft.icons.RESTART_ALT,
            #     bottom=0,
            #     right=0,
            #     on_click=self.reset_settings,
            #     mini=True,
            # ),
        ]

    def reset_settings(self, e):
        self.client_storage.clear()
        self.page.window_destroy()

    def search(self, e):
        query = self.field.value

        if not len(query):
            return
        elif len(query) < 4:
            self.field.error_text = "Слишком короткий запрос"
            self.field.update()
            return

        self.loading.visible = self.field.disabled = True
        self.results.visible = False
        self.update()

        self.client_storage.set(Keys.last_query, query)

        self.results.controls = [
            Result(index=index + 1, **result_kwargs)
            for index, result_kwargs in enumerate(self.driver.search(query))
        ]

        self.loading.visible = self.field.disabled = False
        self.results.visible = True
        self.update()

        self.driver.open_search()
