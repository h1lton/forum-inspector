from asyncio import sleep

import flet as ft
from flet_core import (
    UserControl,
    icons,
    CrossAxisAlignment,
    MainAxisAlignment,
    colors,
    Container,
    MaterialState,
    IconButton,
    TextField,
    padding,
    margin,
    Ref,
    Icon,
    Stack,
    FontWeight,
)

from config import Config
from parser import Parser
from views import View


class ResultPrefix(ft.Container):
    def __init__(self, name: str):
        super().__init__()

        text = ft.Text(value=name, size=10, weight=FontWeight.W_500)

        self.content = text
        self.border_radius = 6
        self.padding = 5

        if name == "ОДОБРЕНО":
            self.bgcolor = colors.GREEN_900
            text.color = colors.WHITE70
        elif name == "ОТКАЗАНО":
            self.bgcolor = colors.RED_900
            text.color = colors.WHITE70
        else:
            self.bgcolor = colors.BLUE_900
            text.color = colors.WHITE70


class SearchResult(UserControl):
    def __init__(
        self,
        prefix: str | None,
        user: str,
        date: str,
        chapter: str,
        link: str,
    ):
        super().__init__()

        self.link = link
        self.user = user
        self.chapter = chapter

        self.title = ft.Row(
            [ft.Text(date, weight=FontWeight.W_600)],
        )

        if prefix:
            self.title.controls.insert(0, ResultPrefix(prefix))

    async def launch_url(self, e):
        await self.page.launch_url_async(self.link)

    def build(self):
        return Container(
            ft.OutlinedButton(
                content=Container(
                    ft.Column(
                        controls=[
                            self.title,
                            ft.Row(
                                [
                                    ft.Column(
                                        controls=[
                                            ft.Row(
                                                [
                                                    ft.Text(
                                                        "Автор:",
                                                        opacity=0.3,
                                                    ),
                                                    ft.Text(self.user),
                                                ],
                                                spacing=5,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Text(
                                                        "Раздел:",
                                                        opacity=0.3,
                                                    ),
                                                    ft.Text(
                                                        self.chapter,
                                                        opacity=0.5,
                                                    ),
                                                ],
                                                spacing=5,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                            ),
                        ],
                        spacing=3,
                    ),
                    padding=padding.only(
                        left=40,
                        top=15,
                        bottom=15,
                    ),
                    on_click=self.launch_url,
                ),
                style=ft.ButtonStyle(
                    color=colors.ON_BACKGROUND,
                    padding=0,
                    shape=ft.RoundedRectangleBorder(radius=0),
                    side=ft.BorderSide(width=-1),
                    overlay_color=colors.with_opacity(0.05, colors.ON_BACKGROUND),
                ),
            ),
            # margin=margin.only(left=15, right=51, top=5, bottom=5),
            # border_radius=10,
        )


class SearchView(UserControl):
    def __init__(self, config: Config):
        super().__init__(width=550)

        self.config = config
        self.parser = Parser(config)

        self.field = Ref[TextField]()
        self.results = ft.Column(
            expand=1,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )
        self.loading = Ref[Container]()
        self.error_container = Ref[Container]()
        self.error_text = Ref[ft.Text]()

    def build(self):
        return ft.Column(
            [
                Container(
                    content=TextField(
                        border_radius=25,
                        border_width=0,
                        border_color=colors.TRANSPARENT,
                        ref=self.field,
                        value=self.config.last_query,
                        on_submit=self.search,
                        hint_text="Поиск...",
                        prefix=Container(width=30),
                        content_padding=0,
                        text_size=16,
                        hint_style=ft.TextStyle(
                            color=colors.with_opacity(
                                0.5, colors.ON_SECONDARY_CONTAINER
                            ),
                        ),
                        text_style=ft.TextStyle(
                            weight=ft.FontWeight.W_500,
                        ),
                        filled=True,
                        on_focus=self.on_focus_field,
                    ),
                    margin=margin.only(top=10, left=10, right=10),
                ),
                Stack(
                    [
                        Container(
                            ft.ProgressRing(),
                            alignment=ft.alignment.center,
                            ref=self.loading,
                            visible=False,
                        ),
                        self.results,
                        ft.Row(
                            [
                                Container(
                                    content=ft.Row(
                                        [
                                            Icon(
                                                icons.ERROR_OUTLINE,
                                                color=colors.ON_ERROR_CONTAINER,
                                            ),
                                            ft.Text(
                                                ref=self.error_text,
                                                color=colors.ON_ERROR_CONTAINER,
                                                weight=ft.FontWeight.W_500,
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                    ref=self.error_container,
                                    bgcolor=colors.ERROR_CONTAINER,
                                    padding=5,
                                    border_radius=10,
                                    opacity=1,
                                    margin=margin.only(left=30, top=10),
                                    animate_opacity=300,
                                    visible=False,
                                )
                            ]
                        ),
                    ],
                    expand=1,
                ),
            ],
            spacing=0,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )

    async def on_focus_field(self, e):
        if self.error_container.current.visible:
            self.error_container.current.opacity = 0
            await self.error_container.current.update_async()
            await sleep(0.3)
            self.error_container.current.opacity = 1
            self.error_container.current.visible = False
            await self.error_container.current.update_async()

    async def search(self, e):
        query = self.field.current.value

        if not len(query):
            return
        elif len(query) < 4:
            self.error_container.current.visible = True
            self.error_text.current.value = "Слишком короткий запрос"
            await self.error_container.current.update_async()
            return

        self.loading.current.visible = self.field.current.disabled = True
        self.results.visible = False
        self.results.controls = []
        await self.update_async()

        self.config.last_query = query

        await sleep(0)
        for result_data in await self.parser.search(query):
            self.results.controls.append(SearchResult(**result_data))

        self.loading.current.visible = self.field.current.disabled = False
        self.results.visible = True
        await self.update_async()


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
                MaterialState.DEFAULT: colors.with_opacity(0.3, colors.ON_BACKGROUND),
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
        self, config: Config, views: list[View], view_container, selected: int = 0
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
        self.btn_size = 48

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
                                        content=Icon(icons.COLOR_LENS_OUTLINED),
                                        style=self.button_style,
                                        width=self.btn_size,
                                        height=self.btn_size,
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
            padding=10,
            width=68,
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
            width=self.btn_size,
            height=self.btn_size,
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
        self.view_container.content = self.views[self.selected].view

        await self.page.update_async()
