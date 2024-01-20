from time import sleep

from flet_core import ControlEvent
from selenium.webdriver import Chrome
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import flet as ft

url = "https://forum.radmir.games/asd"

key_prefix = "forum_inspector."

key_chrome_location = key_prefix + "loc_chrome"
key_last_query = key_prefix + "last_query"

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")


class App:
    def start_up(self, page: ft.Page):
        self.page = page

        page.title = "Forum Inspector"
        page.window_height = 700
        page.window_width = 1000
        page.window_min_height = 350
        page.window_min_width = 500

        self.info = ft.Text("Запускаем приложение", text_align=ft.TextAlign.CENTER)

        self.loading_view = ft.Column(
            [
                self.info,
                ft.Image("loading.gif", height=391 / 5, width=498 / 5),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.main = ft.Container(
            content=self.loading_view,
            right=1,
            left=1,
            bottom=1,
            top=1,
        )

        self.reset_btn = ft.FloatingActionButton(
            icon=ft.icons.RESTART_ALT,
            bottom=0,
            right=0,
            on_click=self.reset_settings,
        )

        page.add(
            ft.Row(
                [ft.Text(value=page.title, style="headlineMedium")],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Stack(
                [
                    self.main,
                    self.reset_btn,
                ],
                expand=1,
            ),
        )

        self.open_forum()

    def destroy(self):
        if hasattr(self, "driver"):
            self.driver.quit()

    def reset_settings(self, e: ControlEvent):
        keys = self.page.client_storage.get_keys(key_prefix)
        for key in keys:
            self.page.client_storage.remove(key)
        self.page.window_destroy()

    def loading(self, message):
        self.info.value = message
        self.loading_view.visible = True
        return self.loading_view

    def search(self, e: ControlEvent):
        query = e.control.value

        if len(query) < 4:
            self.search_field.error_text = "Слишком короткий запрос"
            self.search_field.update()
            return

        self.page.client_storage.set(key_last_query, query)

        self.search_view.controls[1] = self.loading("Ищем")
        self.search_view.update()

        while True:
            try:
                self.driver.find_element(By.ID, "QuickSearchPlaceholder").click()
                elem = self.driver.find_element(By.NAME, "keywords")
                elem.send_keys(query, Keys.RETURN)
                break
            except NoSuchElementException:
                pass

        while self.driver.current_url == url:
            pass

        msg = self.driver.find_element(
            By.CSS_SELECTOR, ".searchResultsList > li:first-child > div.listBlock.main"
        )

        msg_link = msg.find_element(
            By.CSS_SELECTOR, "div.titleText > h3 > a"
        ).get_attribute("href")
        msg_date = msg.find_element(By.CSS_SELECTOR, "div.meta > .DateTime").text

        self.info.value = (
            f"Последняя тема с упоминанием {query}:\n\n{msg_date}\n{msg_link}"
        )

        self.search_view.controls[1] = self.info
        self.search_view.update()

    def open_forum(self):
        self.main.content = self.loading("Открываем браузер")
        self.main.update()

        chrome_location = self.page.client_storage.get(key_chrome_location)
        if chrome_location:
            chrome_options.binary_location = chrome_location

        try:
            self.driver = Chrome(options=chrome_options)

            self.main.content = self.loading("Открываем форум")
            self.main.update()

            self.driver.get(url)

            def change_text(e):
                self.search_field.error_text = None
                self.search_field.update()

            self.search_field = ft.TextField(
                value=self.page.client_storage.get(key_last_query),
                width=300,
                label="Поиск...",
                on_submit=self.search,
                on_change=change_text,
            )
            self.info.value = None
            self.search_view = ft.Column(
                [
                    self.search_field,
                    self.info,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
            )

            self.main.content = self.search_view
            self.main.update()

        except WebDriverException as exp:
            if exp.msg != "unknown error: cannot find Chrome binary":
                raise exp

            self.info.value = "Укажите путь к Chrome"

            def pick_file(e: ControlEvent):
                if not e.files:
                    return

                file = e.files[0]

                if file.name == "chrome.exe":
                    self.page.client_storage.set(key_chrome_location, file.path)
                    self.open_forum()

            file_picker = ft.FilePicker(on_result=pick_file)
            self.page.overlay.append(file_picker)
            btn_pick_file = ft.FloatingActionButton(
                icon=ft.icons.FILE_OPEN,
                on_click=lambda e: file_picker.pick_files(),
            )

            self.main.content = ft.Column(
                [
                    self.info,
                    btn_pick_file,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.page.update()


if __name__ == "__main__":
    app = App()
    ft.app(app.start_up)
    app.destroy()
