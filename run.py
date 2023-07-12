import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class QuotesScraper:
    def __init__(self):
        load_dotenv()
        self.user = str(os.getenv("PROXY")).split(":")[0]
        self.password = str(os.getenv("PROXY")).split(":")[1].split("@")[0]
        with open(".env") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                self.port = str(lines[1].strip())
        self.proxy = str(os.getenv("PROXY")).split("@")[1] + self.port
        self.input_url = os.getenv("INPUT_URL")
        self.output_file = os.getenv("OUTPUT_FILE")
        self.proxies = {
            "http": f"http://{self.user}:{self.password}@{self.proxy}",
            "https": f"http://{self.user}:{self.password}@{self.proxy}",
        }

    def page_scrape(self, url):
        response = requests.get(url, proxies=self.proxies)
        soup = BeautifulSoup(response.text, "html.parser")
        data_to_scrap = (
            soup.find_all("script")[1]
            .text.split("for (var i in data)")[0]
            .split("var data =")[-1]
            .strip()
            .rstrip(";")
        )
        return json.loads(data_to_scrap)

    def quote_scrape(self):
        url = self.input_url
        quotes = []
        while True:

            for element in self.page_scrape(url):
                text = element["text"]
                by = element["author"]["name"]
                tags = element["tags"]
                quotes.append({"text": text, "by": by, "tags": tags})

            next_page = BeautifulSoup(requests.get(url).text, "html.parser").find(
                "li", {"class": "next"}
            )
            if not next_page:
                break
            else:
                page_number = next_page.find("a").get("href").split("js-delayed/")[1]
                url = self.input_url + page_number
        return quotes

    def save_quotes(self, quotes):
        with open(self.output_file, mode="w", encoding="utf-8") as f:
            json.dump(quotes, f, indent=1, separators=(",", ":"))

    def trigger(self):
        quotes = self.quote_scrape()
        self.save_quotes(quotes)


if __name__ == "__main__":
    scraper = QuotesScraper()
    scraper.trigger()
