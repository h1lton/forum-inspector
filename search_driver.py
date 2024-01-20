from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome, Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class SearchDriver:
    def __init__(self, driver_path: str):
        self.options = Options()
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--headless=new")
        self.options.add_argument("--disable-gpu")
        self.options.binary_location = driver_path

    def start_up(self):
        """Запускает драйвер."""
        self.driver = Chrome(options=self.options)

    def open_search(self):
        """Открывает форум."""
        self.driver.get("https://forum.radmir.games/search/?type=post")

    def search(self, query: str):
        elem = WebDriverWait(self.driver, 15).until(
            ec.presence_of_element_located((By.NAME, "keywords"))
        )

        elem.send_keys(query, Keys.RETURN)

        title = self.driver.title
        WebDriverWait(self.driver, 15).until_not(ec.title_is(title))

        return self.get_results()

    def get_results(self):
        elems = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#content > div.pageWidth > div > div.section.sectionMain.searchResults > form > ol > li > div.listBlock.main",
        )
        results = [self.parse_result(elem) for elem in elems]
        return results

    @staticmethod
    def find_element_or_none(element: WebElement, by: By, value: str):
        try:
            return element.find_element(by, value)
        except NoSuchElementException:
            return None

    def parse_result(self, result: WebElement):
        prefix_elem = self.find_element_or_none(
            result,
            By.CSS_SELECTOR,
            "div.titleText > h3 > a > span",
        )
        prefix = prefix_elem.text if prefix_elem else None

        link = result.find_element(
            By.CSS_SELECTOR, "div.titleText > h3 > a"
        ).get_attribute("href")

        user, date, chapter = [
            elem.text for elem in result.find_elements(By.CSS_SELECTOR, "div.meta > *")
        ]

        return {
            "prefix": prefix,
            "user": user,
            "date": date,
            "chapter": chapter,
            "link": link,
        }

    def destroy(self):
        self.driver.quit()
