from asyncio import sleep

import flet as ft
from flet_core import colors

from src.backend.parser import Parser
from src.config import Config
from src.controls import ViewContainer
from src.search import constants


class ResultPrefix(ft.Container):
    def __init__(self, name: str):
        super().__init__()

        text = ft.Text(value=name, size=10, weight=ft.FontWeight.W_500)

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


class SearchResult(ft.UserControl):  # TODO: переделать
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
            [ft.Text(date, weight=ft.FontWeight.W_600)],
        )

        if prefix:
            self.title.controls.insert(0, ResultPrefix(prefix))

    async def launch_url(self, e):
        await self.page.launch_url_async(self.link)

    def build(self):
        return ft.Container(
            ft.OutlinedButton(
                content=ft.Container(
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
                    padding=ft.padding.only(
                        left=constants.RESULT_LEFT_PADDING,
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
                    overlay_color=colors.with_opacity(
                        0.05, colors.ON_BACKGROUND
                    ),
                ),
            ),
            # margin=margin.only(left=15, right=51, top=5, bottom=5),
            # border_radius=10,
        )


class SearchView(ViewContainer):
    def __init__(self, config: Config):
        super().__init__(icon=ft.icons.SEARCH_ROUNDED)

        self.config = config
        self.parser = Parser(config)
        self.is_loading_items = False
        self.next_page = None

        self.results = ft.ListView(
            expand=1,
            spacing=0,
            on_scroll_interval=0,
            on_scroll=self.on_scroll,
        )
        self.field = ft.Ref[ft.TextField]()
        self.loading = ft.Ref[ft.Container]()
        self.error_container = ft.Ref[ft.Container]()
        self.error_text = ft.Ref[ft.Text]()

    def build(self):
        return ft.Column(
            [
                ft.Container(
                    content=ft.TextField(
                        border_radius=25,
                        border_width=0,
                        border_color=colors.TRANSPARENT,
                        ref=self.field,
                        value=self.config.last_query,
                        on_submit=self.search,
                        hint_text="Поиск...",
                        prefix=ft.Container(width=constants.FIELD_PREFIX),
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
                    margin=ft.margin.only(
                        left=constants.MAIN_PADDING,
                        top=constants.MAIN_PADDING,
                        right=constants.MAIN_PADDING,
                    ),
                ),
                ft.Stack(
                    [
                        ft.Container(
                            ft.ProgressRing(),
                            alignment=ft.alignment.center,
                            ref=self.loading,
                            visible=False,
                        ),
                        self.results,
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.icons.ERROR_OUTLINE,
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
                                    margin=ft.margin.only(
                                        left=constants.RESULT_LEFT_PADDING,
                                        top=10,
                                    ),
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
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    async def on_scroll(self, e: ft.OnScrollEvent):
        count_results = len(self.results.controls)

        if (
            e.event_type == "start"
            and e.pixels
            > e.max_scroll_extent * (count_results - 4) / count_results
            and not self.is_loading_items
            and self.next_page
        ):
            self.is_loading_items = True

            self.results.controls.append(
                ft.Container(
                    ft.ProgressRing(height=20, width=20, stroke_width=3),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=10, bottom=10),
                )
            )
            await self.results.update_async()

            self.results.controls.pop()

            self.next_page, generator = await self.parser.load_data(
                "/" + self.next_page
            )
            for result_data in generator:
                self.results.controls.append(SearchResult(**result_data))

            await self.update_async()
            self.is_loading_items = False

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
        await self.results.clean_async()
        self.is_loading_items = False
        await self.update_async()

        self.config.last_query = query

        self.next_page, generator = await self.parser.search(query)
        for result_data in generator:
            self.results.controls.append(SearchResult(**result_data))

        self.loading.current.visible = self.field.current.disabled = False
        self.results.visible = True
        await self.update_async()
