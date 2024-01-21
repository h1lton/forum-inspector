from time import time

from bs4 import BeautifulSoup, Tag
import requests

from client_storage import ClientStorage
from reaclab_bypass import ReactLabBypass
from search.result import Result


class Backend:
    def __init__(self, client_storage: ClientStorage):
        self.site = "https://forum.radmir.games"
        self.rlb = ReactLabBypass(self.site, client_storage=client_storage)

    @property
    def cookies(self):
        return self.rlb.get_cookie()

    def search(self, query: str) -> list[Result]:
        headers = {
            "origin": self.site,
            "referer": self.site,
        }
        data = {
            "keywords": query,
            "date": None,
            "order": "date",
            "type": "post",
        }
        response = requests.post(
            self.site + "/search/search",
            headers=headers,
            cookies=self.cookies,
            data=data,
        )

        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        for index, result in enumerate(soup.find_all("div", class_="listBlock main")):
            prefix_elem: Tag = result.find("span", class_="prefix")
            prefix = prefix_elem.text if prefix_elem else None
            link = self.site + "/" + result.css.select_one("h3.title > a")["href"]

            user, date, chapter = [
                tag.string
                for tag in result.find("div", class_="meta").children
                if isinstance(tag, Tag)
            ]

            results.append(
                Result(
                    index=index + 1,
                    prefix=prefix,
                    link=link,
                    user=user,
                    date=date,
                    chapter=chapter,
                )
            )

        return results
