import atexit
import locale
from asyncio import sleep

import flet as ft
from flet_core import colors, icons

from config import Config
from controls import SearchView, WindowTitleBar, NavigationMenu
from views import View


class App:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, "ru_RU")
        self.config = Config()
        atexit.register(self.destroy)

    async def start_up(self, page: ft.Page):
        page.title = "Forum Inspector"
        page.window_width = 634
        page.window_height = 816
        page.window_frameless = True
        page.window_bgcolor = ft.colors.TRANSPARENT
        page.bgcolor = ft.colors.TRANSPARENT
        page.window_resizable = False
        page.padding = 0
        page.spacing = 0
        page.theme_mode = self.config.theme_mode
        page.theme = page.dark_theme = ft.Theme(
            color_scheme_seed=self.config.color_scheme_seed
        )

        await page.window_center_async()

        self.views = [
            View(
                name="search",
                view=SearchView(self.config),
                icon=icons.SEARCH_ROUNDED,
            ),
            View(
                name="follow",
                view=ft.Container(
                    ft.Text("Отслеживаемые"),
                    alignment=ft.alignment.center,
                    width=550,
                ),
                icon=icons.BOOKMARK_BORDER_ROUNDED,
                selected_icon=icons.BOOKMARK_ROUNDED,
            ),
            View(
                name="check",
                view=ft.Container(
                    ft.Text("Отложенные"),
                    alignment=ft.alignment.center,
                    width=550,
                ),
                icon=icons.ACCESS_TIME_ROUNDED,
                selected_icon=icons.ACCESS_TIME_FILLED_ROUNDED,
            ),
        ]
        view_container = ft.Container(
            self.views[0].view,
            bgcolor=colors.with_opacity(0.1, colors.OUTLINE),
            border_radius=ft.border_radius.only(top_left=10),
        )

        await sleep(0.075)

        await page.add_async(
            ft.Container(
                content=ft.Column(
                    [
                        WindowTitleBar(page, maximizable=False),
                        ft.Row(
                            [
                                NavigationMenu(
                                    self.config,
                                    self.views,
                                    view_container,
                                ),
                                view_container,
                            ],
                            expand=1,
                            spacing=0,
                        ),
                    ],
                    expand=1,
                    spacing=0,
                ),
                bgcolor=ft.colors.BACKGROUND,
                expand=1,
                margin=8,
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    blur_style=ft.ShadowBlurStyle.OUTER,
                    color=ft.colors.with_opacity(0.2, ft.colors.SHADOW),
                ),
            )
        )

    def destroy(self):
        self.config.save_to_file()


if __name__ == "__main__":
    app = App()
    ft.app(target=app.start_up, view=ft.FLET_APP_HIDDEN)
