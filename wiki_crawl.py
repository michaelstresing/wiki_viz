from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse
import requests
from queue import Queue
from graphviz import Graph
from linkutilites import LinkUtil


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
        '''
        Builder method for constructing a Crawler.
        '''
        return BuildCrawler(Crawler.__create_key)

    def retrieve_html(self):
        '''
        Used by the pull_processed_links function, gets the raw html
        '''

        response = requests.get(self.url)
        body = response.content
        soup = bs4(body, "html.parser")

        if 199 < response.status_code < 300:
            return soup
        else:
            assert "Invalid Request"

    @staticmethod
    def pull_processed_links(url):
        '''
        Takes all processed links
        '''

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
                Crawler.process_link_out(link)
            if link:
                page_links.add(link)

        return page_links

    @staticmethod
    def process_link_in(link):
        '''
        Processes the link to ensure that it fits the parameters.
        '''

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
        '''
        Processes link.
        '''

        if not LinkUtil.is_active_link(link):
            return None
        elif not LinkUtil.is_html_link(link):
            return None

        return link

    def establish_graph(self):
        '''
        Initializes a graphviz graph
        :return: the graph object.
        '''

        g = Graph('G',
                  filename=f"network_graphs/{self.url.replace('/', '_').replace(':', '_')}_network.gv'",
                  engine='sfdp'
                  # format='.jpg'
                  )

        return g

    @staticmethod
    def write_relationship(g, parent, child):
        '''
        Creates a graph relationship in graphviz between a parent and a child node. (Creates each as a node
        if they don't already exist.
        '''

        g.edge(f"{parent}", f"{child}")

    def construct_url(self, link):
        """
        Takes a link's path and constucts the full URL based on the original website scheme and domain.
        """
        url = self.url
        parsedurl = urlparse(url)
        return parsedurl[0] + "://" + parsedurl[1] + link

    @staticmethod
    def deconstruct_url(url):
        """
        Takes a link's path and constucts the full URL based on the original website scheme and domain.
        """
        parsedurl = urlparse(url)
        return parsedurl[2]

    @staticmethod
    def view(g):
        '''
        Opens a graphviz.
        '''

        g.view()

    def run_crawler(self):
        '''
        Runs the crawler over all links.
        Finishes by opening the Graph created.
        '''

        q = self._queue
        q.put((self.url, 0))
        g = Crawler.establish_graph(self)

        while q.qsize() > 0:

            item = q.get()
            url = item[0]
            path = Crawler.deconstruct_url(url)
            layer = item[1]
            print(f"Working on layer {layer}")

            links = Crawler.pull_processed_links(url)

            for link in links:
                print(f"Adding {link}")
                fulllink = Crawler.construct_url(self=self, link=link)
                Crawler.write_relationship(g=g, parent=path, child=link)

                if layer <= self.depth:
                    q.put((fulllink, layer + 1))

        print("Success!")
        Crawler.view(g)


class BuildCrawler:

    def __init__(self, create_key, url: str = "https://en.wikipedia.org/wiki/Tim_Berners-Lee", depth: int = 2):
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
testc.with_url('https://en.wikipedia.org/wiki/')
testc = testc.to_crawler()

testc.run_crawler()
