from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup, Tag

from src.config import Config
from src.backend.reaclab_bypass import ReactLabBypass


class Parser:
    def __init__(self, config: Config):
        self.site = "https://forum.radmir.games"
        self.session = aiohttp.ClientSession(base_url=self.site)
        self.rlb = ReactLabBypass(config, self.session)

    @staticmethod
    def get_date(tag: Tag):
        if tag.name != "abbr":
            return tag.text

        date = datetime.fromtimestamp(int(tag["data-time"]))

        diff = int(tag["data-diff"])
        if diff < 60:
            return "только что"
        elif diff < 120:
            return "минуту назад"
        elif diff < 3600:
            return f"{diff // 60} мин. назад"
        elif diff < 86400:
            return date.strftime("Сегодня, в %H:%M")
        elif diff < 172800:
            return date.strftime("Вчера, в %H:%M")
        else:
            return date.strftime("%A в %H:%M").capitalize()

    def generator_data(self, soup):
        for result in soup.find_all("div", class_="listBlock main"):
            prefix_elem: Tag = result.find("span", class_="prefix")
            prefix = prefix_elem.text if prefix_elem else None
            link = self.site + "/" + result.css.select_one("h3.title > a")["href"]

            div_meta = result.find("div", class_="meta").contents

            user = div_meta[1].text
            date = self.get_date(div_meta[3])
            chapter = div_meta[5].text

            yield {
                "prefix": prefix,
                "link": link,
                "user": user,
                "date": date,
                "chapter": chapter,
            }

    async def search(self, query: str):
        data = {
            "keywords": query,
            "date": None,
            "order": "date",
            "type": "post",
        }
        return await self.load_data("/search/search", data)

    async def load_data(self, url, data=None):
        await self.rlb.set_cookie()
        response = (
            await self.session.post(url, data=data)
            if data
            else await self.session.get(url)
        )

        soup = BeautifulSoup(await response.text(), "html.parser")

        next_page = soup.find("a", class_="nextLink")
        if next_page:
            next_page = next_page["href"]

        return next_page, self.generator_data(soup)
