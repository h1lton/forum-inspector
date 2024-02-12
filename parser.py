import aiohttp
from bs4 import BeautifulSoup, Tag

from config import Config
from reaclab_bypass import ReactLabBypass


class Parser:
    def __init__(self, config: Config):
        self.site = "https://forum.radmir.games"
        self.session = aiohttp.ClientSession(base_url=self.site)
        self.rlb = ReactLabBypass(config, self.session)

    def generator_data(self, soup):
        for result in soup.find_all("div", class_="listBlock main"):
            prefix_elem: Tag = result.find("span", class_="prefix")
            prefix = prefix_elem.text if prefix_elem else None
            link = self.site + "/" + result.css.select_one("h3.title > a")["href"]

            # print(
            #     result.find("div", class_="meta").contents[3]
            # )  # todo: Сделать адекватное отображение даты

            user, date, chapter = [
                tag.text
                for tag in result.find("div", class_="meta").children
                if isinstance(tag, Tag)
            ]

            yield {
                "prefix": prefix,
                "link": link,
                "user": user,
                "date": date,
                "chapter": chapter,
            }

    async def search(self, query: str):
        await self.rlb.set_cookie()
        data = {
            "keywords": query,
            "date": None,
            "order": "date",
            "type": "post",
        }
        response = await self.session.post(
            "/search/search",
            data=data,
        )

        soup = BeautifulSoup(await response.text(), "html.parser")

        return self.generator_data(soup)
