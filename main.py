import atexit

import flet as ft

from client_storage import ClientStorage, Keys
from controls.loading import Loading
from controls.search.view import SearchView
from search_driver import SearchDriver


class App:
    def __init__(self):
        self.driver: SearchDriver | None = None
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

        # Проверяем наличие пути к драйверу в хранилище
        self.driver_path = self.client_storage.get(Keys.driver_path)
        if self.driver_path:
            self.loading_app()
        else:
            self.driver_path_request()

    def driver_path_request(self):
        """Запрашивает у пользователя путь до Chrome."""

        def file_picker_result(e: ft.FilePickerResultEvent):
            if not e.files:
                return

            file = e.files[0]

            if file.name == "chrome.exe":
                self.client_storage.set(Keys.driver_path, file.path)
                self.page.overlay.remove(file_picker)
                dialog.open = False
                self.page.update()

                self.driver_path = file.path

                self.loading_app()

        file_picker = ft.FilePicker(on_result=file_picker_result)

        dialog = ft.AlertDialog(
            title=ft.Text("Укажите путь до Chrome"),
            content=ft.FloatingActionButton(
                icon=ft.icons.FOLDER_OPEN,
                on_click=lambda e: file_picker.pick_files(),
            ),
            modal=True,
            open=True,
        )

        self.page.overlay.append(file_picker)
        self.page.dialog = dialog
        self.page.update()

    def loading_app(self):
        """Загружает приложение."""
        self.driver = SearchDriver(self.driver_path)

        self.loading_view = Loading("Запускаем драйвер")
        self.page.add(self.loading_view)
        self.driver.start_up()

        self.loading_view.update_status("Отрываем форум")
        self.driver.open_search()

        self.search_view = SearchView(self.driver, self.client_storage)
        self.loading_view.visible = False
        self.page.add(self.search_view)

    def destroy(self):
        print("destroy")
        if self.driver:
            self.driver.destroy()


if __name__ == "__main__":
    app = App()
    atexit.register(app.destroy)
    ft.app(target=app.start_up, view=ft.FLET_APP_HIDDEN)
