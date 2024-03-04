import flet as ft
from flet_core import (
    icons,
    CrossAxisAlignment,
    MainAxisAlignment,
    colors,
    Container,
    MaterialState,
    IconButton,
    Icon,
)

from src import constants
from src.config import Config


class ViewContainer(ft.UserControl):
    def __init__(self, icon: str, selected_icon: str | None = None):
        super().__init__(width=constants.VIEW_WIDTH)

        self.icon = icon
        self.selected_icon = selected_icon


class WindowTitleBar(ft.Row):
    btn_maximize = ft.Ref[IconButton]()

    def __init__(self, page: ft.Page, maximizable: bool = True):
        page.on_window_event = self.on_window_event
        self.page = page
        self.maximizable = maximizable
        super().__init__(
            spacing=0,
            height=30,
            controls=[
                ft.WindowDragArea(
                    Container(
                        ft.Row(
                            [
                                Container(
                                    ft.Image(
                                        src="logo.svg",
                                        color=colors.OUTLINE,
                                    ),
                                    width=30,
                                    height=30,
                                    padding=7,
                                ),
                                ft.Text(
                                    self.page.title,
                                    color=colors.OUTLINE,
                                    theme_style=ft.TextThemeStyle.TITLE_SMALL,
                                ),
                            ],
                            spacing=0,
                        ),
                    ),
                    expand=True,
                ),
                IconButton(
                    icons.HORIZONTAL_RULE_OUTLINED,
                    on_click=self.minimize,
                    icon_size=15.2,
                    style=self.btn_style(),
                    width=40,
                ),
                IconButton(
                    icons.CHECK_BOX_OUTLINE_BLANK_OUTLINED,
                    on_click=self.maximize,
                    icon_size=13.6,
                    style=self.btn_style(),
                    ref=self.btn_maximize,
                    width=40,
                    visible=self.maximizable,
                ),
                IconButton(
                    icons.CLOSE_OUTLINED,
                    on_click=self.finalize,
                    icon_size=17.6,
                    style=self.btn_style(True),
                    width=40,
                ),
            ],
        )

    async def maximize(self, e):
        self.page.window_maximized = not self.page.window_maximized
        await self.page.update_async()

    async def minimize(self, e):
        self.page.window_minimized = True
        await self.page.update_async()

    async def finalize(self, e):
        await self.page.window_close_async()

    @staticmethod
    def btn_style(is_close_btn: bool = False):
        return ft.ButtonStyle(
            color={
                MaterialState.DEFAULT: colors.with_opacity(
                    0.3, colors.ON_BACKGROUND
                ),
                MaterialState.HOVERED: colors.ON_BACKGROUND,
            },
            padding=0,
            shape=ft.RoundedRectangleBorder(radius=0),
            overlay_color=colors.RED if is_close_btn else None,
        )

    async def on_window_event(self, e):
        if e.data == "close":
            await self.page.window_close_async()
        elif e.data == "unmaximize" or e.data == "maximize":
            if self.page.window_maximized:
                self.btn_maximize.current.icon = ft.icons.FILTER_NONE
                self.btn_maximize.current.icon_size = 12
            else:
                self.btn_maximize.current.icon = (
                    ft.icons.CHECK_BOX_OUTLINE_BLANK_ROUNDED
                )
                self.btn_maximize.current.icon_size = 13.6
            await self.btn_maximize.current.update_async()


class MenuColorItem(ft.MenuItemButton):
    def __init__(self, color, name, config: Config):
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Icon(name=ft.icons.COLOR_LENS_OUTLINED, color=color),
                    ft.Text(name),
                ],
            ),
            on_click=self.seed_color_changed,
            data=color,
        )

        self.config = config

    async def seed_color_changed(self, e):
        self.config.color_scheme_seed = self.data
        self.page.theme = self.page.dark_theme = ft.theme.Theme(
            color_scheme_seed=self.data
        )
        await self.page.update_async()


class NavigationMenu(Container):
    def __init__(
        self,
        config: Config,
        views: list[ViewContainer],
        view_container,
        selected: int = 0,
    ):
        self.config = config
        self.selected = selected
        self.views = views
        self.view_container = view_container
        self.button_style = ft.ButtonStyle(
            bgcolor={ft.MaterialState.SELECTED: colors.SECONDARY_CONTAINER},
            color={
                ft.MaterialState.DEFAULT: colors.ON_BACKGROUND,
                ft.MaterialState.SELECTED: colors.ON_SECONDARY_CONTAINER,
            },
            # padding=0,
            shape=ft.RoundedRectangleBorder(radius=10),
            overlay_color=colors.with_opacity(0.3, colors.SECONDARY_CONTAINER),
        )
        self.view_buttons = ft.Column()

        for i, view in enumerate(views):
            self.view_buttons.controls.append(
                self.navigation_button(
                    view.icon,
                    selected_icon=view.selected_icon,
                    on_click=self.selected_view,
                    data=i,
                    selected=i == selected,
                )
            )

        super().__init__(
            content=ft.Column(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    self.view_buttons,
                    ft.Column(
                        [
                            self.navigation_button(
                                icon=icons.BRIGHTNESS_2_OUTLINED,
                                on_click=self.theme_changed,
                            ),
                            ft.MenuBar(
                                [
                                    ft.SubmenuButton(
                                        controls=[
                                            self.menu_item(
                                                color="deeppurple",
                                                name="Deep purple",
                                            ),
                                            self.menu_item(
                                                color="indigo",
                                                name="Indigo",
                                            ),
                                            self.menu_item(
                                                color="blue",
                                                name="Blue (default)",
                                            ),
                                            self.menu_item(
                                                color="teal",
                                                name="Teal",
                                            ),
                                            self.menu_item(
                                                color="green",
                                                name="Green",
                                            ),
                                            self.menu_item(
                                                color="yellow",
                                                name="Yellow",
                                            ),
                                            self.menu_item(
                                                color="orange",
                                                name="Orange",
                                            ),
                                            self.menu_item(
                                                color="deeporange",
                                                name="Deep orange",
                                            ),
                                            self.menu_item(
                                                color="pink",
                                                name="Pink",
                                            ),
                                        ],
                                        content=Icon(
                                            icons.COLOR_LENS_OUTLINED
                                        ),
                                        style=self.button_style,
                                        width=constants.NAV_BTN_SIZE,
                                        height=constants.NAV_BTN_SIZE,
                                    )
                                ],
                                style=ft.MenuStyle(
                                    padding=0,
                                    surface_tint_color=colors.TRANSPARENT,
                                    bgcolor=colors.TRANSPARENT,
                                    shadow_color=colors.TRANSPARENT,
                                ),
                            ),
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                ],
            ),
            padding=constants.MAIN_PADDING,
            width=constants.NAV_WIDTH,
        )

    def navigation_button(
        self,
        icon: str,
        selected_icon: str | None = None,
        on_click=None,
        data=None,
        selected: bool = False,
    ):
        return IconButton(
            icon=icon,
            selected_icon=selected_icon,
            on_click=on_click,
            data=data,
            selected=selected,
            style=self.button_style,
            width=constants.NAV_BTN_SIZE,
            height=constants.NAV_BTN_SIZE,
        )

    async def theme_changed(self, e: ft.ControlEvent):
        if self.page.theme_mode == "light":
            self.config.theme_mode = self.page.theme_mode = "dark"
            e.control.icon = icons.BRIGHTNESS_2_OUTLINED
        else:
            self.config.theme_mode = self.page.theme_mode = "light"
            e.control.icon = icons.WB_SUNNY_OUTLINED
        await self.page.update_async()

    def menu_item(self, color, name):
        return MenuColorItem(
            color=color,
            name=name,
            config=self.config,
        )

    async def selected_view(self, e):
        e.control.selected = True
        e.control.disabled = True
        btn = self.view_buttons.controls[self.selected]
        btn.selected = False
        btn.disabled = False
        self.selected = e.control.data
        self.view_container.content = self.views[self.selected]

        await self.page.update_async()
