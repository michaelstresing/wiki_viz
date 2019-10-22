from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse
import requests
from queue import Queue
from graphviz import Graph


class LinkUtil:

    @staticmethod
    def is_anchor(link):
        if len(link) > 0 and link[0] == '#':
            return True
        else:
            return False

    @staticmethod
    def is_wiki_link(link):
        return len(link) > 0 and link[0:6] == '/wiki/'

    @staticmethod
    def is_wiki_special_type(link):
        return len(link) > 0 and (link[6:15] == 'Category:'
                                  or link[6:14] == 'Special:'
                                  or link[6:11] == 'Talk:'
                                  or link[6:11] == 'Help:'
                                  or link[6:11] == 'File:'
                                  )

    @staticmethod
    def is_image(link):
        return len(link) > 0 and (link[:-4] == '.png'
                                  or link[:-4] == '.jpg'
                                  or link[:-5] == '.jpeg'
                                  )

    @staticmethod
    def is_active_link(link):
        r = requests.get(link)
        return 199 < r.status_code < 300

    @staticmethod
    def is_html_link(link):
        r = requests.get(link)
        h = r.headers['Content-Type']
        return h[0:9] == 'text/html'


class Crawler:

    def __init__(self, create_key, url, depth):

        assert (create_key == Crawler.__create_key),\
            "A Crawler object must be constructed using the .new() method."

        self.url = url
        self.depth = depth
        self._queue = Queue()

    __create_key = object()

    @classmethod
    def new(cls):
        return BuildCrawler(Crawler.__create_key)

    def retrieve_html(self):

        response = requests.get(self.url)
        body = response.content
        soup = bs4(body, "html.parser")

        if 199 < response.status_code < 300:
            return soup
        else:
            assert "Invalid Request"

    @staticmethod
    def pull_processed_links(url):

        response = requests.get(url)
        body = response.content
        soup = bs4(body, "html.parser")

        if 199 < response.status_code < 300:
            pass
        else:
            assert "Invalid Request"

        page_links = set()
        all_links = [a.get('href') for a in soup.find_all("a", href=True)]

        for link in all_links:
            link = Crawler.process_link_in(link)
            if link:
                page_links.add(link)

        return page_links

    @staticmethod
    def process_link_in(link):

        if LinkUtil.is_anchor(link):
            return None
        elif not LinkUtil.is_wiki_link(link):
            return None
        elif LinkUtil.is_wiki_special_type(link):
            return None
        elif LinkUtil.is_image(link):
            return None

        # more link processing and filtering

        return link

    @staticmethod
    def process_link_out(link):

        if not LinkUtil.is_active_link(link):
            return None
        elif not LinkUtil.is_html_link(link):
            return None

        return link

    def write_relationship(self, parent, child):

        file = f"{self.url.replace('/', '_').replace(':', '_')}_relations.txt"

        with open(f"page_relations/{file}", 'a+') as fout:
            fout.write(f"   {parent} -> {child};\n")

        g = Graph('G', filename=f"{self.url.replace('/', '_').replace(':', '_')}_newtork.gv'", engine='sfdp')

        g.edge({parent}, {child})

    def construct_url(self, link):
        """
        Takes a link's path and constucts the full URL based on the original website scheme and domain.
        """
        url = self.url
        parsedurl = urlparse(url)

        return parsedurl[0] + "://" + parsedurl[1] + link

    def run_crawler(self):

        q = self._queue
        q.put((self.url, 0))

        while q.qsize() > 0:

            item = q.get()
            url = item[0]
            layer = item[1]

            links = Crawler.pull_processed_links(url)

            for link in links:

                fulllink = Crawler.construct_url(self=self, link=link)
                Crawler.write_relationship(self=self, parent=url, child=fulllink)

                if layer < self.depth:
                    q.put((fulllink, layer + 1))


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

testc.run_crawler()
