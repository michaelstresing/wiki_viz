from bs4 import BeautifulSoup as bs4
import requests
from xml.etree import ElementTree


class LinkUtil:

    @staticmethod
    def is_anchor(link):
        return len(link) > 0 and link[0] == '#'

    @staticmethod
    def is_wiki_link(link):
        return len(link) > 0 and link[0:6] == '/wiki/'


class Crawler:

    def __init__(self, create_key, url, depth):

        assert (create_key == Crawler.__create_key),\
            "A Crawler object must be constructed using the .new() method."

        self.url = url
        self.depth = depth

    __create_key = object()

    @classmethod
    def new(cls):
        return BuildCrawler(Crawler.__create_key)

    def retrieve_html(self):

        response = requests.get(self.url)
        body = response.content

        if 199 < response.status_code < 300:
            return body
        else:
            assert "Invalid Request"

    def process_link(self, link):
        if LinkUtil.is_anchor(link):
            return None
        if not LinkUtil.is_wiki_link(link):
            return None

        # more link processing and filtering

        return link

    def pull_raw_links(self, html):

        soup = bs4(html, "html.parser")
        page_links = [a.get('href') for a in soup.find_all("a", href=True)]

        return page_links

    # def extract_broken_links(self, links):
    #
    #     extracted_links = list()
    #
    #     for link in links:
    #         req = requests.get(link)
    #
    #         if 199 < req.status_code < 299:
    #             extracted_links.append(link)
    #
    #     return extracted_links


class BuildCrawler:

    def __init__(self, create_key, url: str = "https://en.wikipedia.org/wiki/Tim_Berners-Lee", depth: int = 3):
        self._create_key = create_key
        self.url = url
        self.depth = depth

    def with_url(self, url):
        """
        Inserts a url.
        """
        self.url = url

    def with_depth(self, depth):
        """
        Inserts a depth value.
        """
        self.depth = depth

    def to_crawler(self):
        """
        Create a Crawler object from the builder
        """
        return Crawler(
            create_key=self._create_key,
            url=self.url,
            depth=self.depth
            )


testc = Crawler.new()
testc = testc.to_crawler()
html = testc.retrieve_html()
testc.pull_links(html)
print(html)