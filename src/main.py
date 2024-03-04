import atexit
import locale
from asyncio import sleep

import flet as ft
from flet_core import colors

import constants
from src.check.controls import CheckView
from src.config import Config
from src.controls import WindowTitleBar, NavigationMenu
from src.follow.controls import FollowView
from src.search.controls import SearchView


class App:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, "ru_RU")
        self.config = Config()
        atexit.register(self.destroy)

    async def start_up(self, page: ft.Page):
        page.title = "Forum Inspector"
        page.window_width = constants.PAGE_WIDTH
        page.window_height = constants.PAGE_HEIGHT
        page.window_frameless = True
        page.window_bgcolor = ft.colors.TRANSPARENT
        page.bgcolor = ft.colors.TRANSPARENT
        page.window_resizable = False
        page.padding = 0
        page.spacing = 0
        page.theme_mode = self.config.theme_mode
        page.theme = page.dark_theme = ft.Theme(
            color_scheme_seed=self.config.color_scheme_seed,
            scrollbar_theme=ft.ScrollbarTheme(cross_axis_margin=5),
        )

        await page.window_center_async()

        self.views = [SearchView(self.config), FollowView(), CheckView()]

        view_container = ft.Container(
            self.views[0],
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
                margin=constants.SHADOW_SIZE,
                shadow=ft.BoxShadow(
                    blur_radius=constants.SHADOW_SIZE,
                    blur_style=ft.ShadowBlurStyle.OUTER,
                    color=ft.colors.with_opacity(0.2, ft.colors.SHADOW),
                ),
            )
        )

    def destroy(self):
        self.config.save_to_file()


if __name__ == "__main__":
    app = App()
    ft.app(
        target=app.start_up,
        view=ft.FLET_APP_HIDDEN,
        assets_dir="../assets",
    )
