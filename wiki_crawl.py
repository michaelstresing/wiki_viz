from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse
import requests
import queue
import os
import numpy
import matplotlib.pyplot as plt
from graphviz import Digraph
import networkx as nx
from linkutilites import LinkUtil


class Crawler:

    __create_key = object()

    def __init__(self, create_key, url, depth, width):

        assert (create_key == Crawler.__create_key),\
            "A Crawler object must be constructed using the .new() method."

        self.url = url
        self.depth = depth
        self.width = width
        self._queue = queue.Queue()

    @classmethod
    def new(cls):
        '''
        Builder method for constructing a Crawler.
        '''
        return BuildCrawler(Crawler.__create_key)

    @staticmethod
    def pull_processed_links(url):
        '''
        Takes all processed links
        '''

        response = requests.get(url)
        page = response.content
        soup = bs4(page, "html.parser")
        body = soup.find(id='bodyContent')

        if 199 < response.status_code < 300:
            pass
        else:
            assert "Invalid Request"

        page_links = set()
        page_links_sanatized = set()
        all_links = [a.get('href') for a in body.find_all("a", href=True)]

        for link in all_links:

            link = Crawler.process_link_in(link)

            if link:
                page_links.add(link)

        for link in list(page_links):

            if "#" in link:

                hashindex = link.index("#")
                sanlink = link[0:hashindex]
                page_links_sanatized.add(sanlink)

        return page_links_sanatized

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

    def construct_url(self, link):
        """
        Takes a link's path and constucts the full URL based on the original website scheme and domain.
        """
        url = self.url
        parsedurl = urlparse(url)
        return parsedurl[0] + "://" + parsedurl[1] + link

    def run_crawler_graphviz(self):
        '''
        Runs the crawler over all links.
        :return: Graph object for graphviz
        '''

        # Setup a queue and add the starting point URL
        q = self._queue
        q.put((self.url, 0))
        graph = Visualization.establish_graph_graphviz(self)

        # Process links and add to queue, whilst queue not empty
        while self._queue.qsize() > 0:

            item = q.get()
            url = item[0]
            path = LinkUtil.deconstruct_url(url)
            layer = item[1]

            if url:
                print(f"Working on layer {layer}")
            links = Crawler.pull_processed_links(url)

            if len(links) > self.width:
                links = numpy.random.choice(list(links), self.width, replace=False)

            for link in links:
                print(f"Adding {link}")
                fulllink = Crawler.construct_url(self=self, link=link)
                Visualization.write_relationship_graphviz(g=graph, parent=path, child=link)

                if layer < self.depth:
                    q.put((fulllink, layer + 1))

        print("Success!")
        Visualization.view_with_graphviz(self, graph)

        return graph

    def run_crawler_plt(self):
        '''
        Runs the crawler over all links.
        :return: Graph object for networkx and pyplot.
        '''

        q = self._queue
        q.put((self.url, 0))
        graph = Visualization.establish_graph_nx()

        while self._queue.qsize() > 0:

            item = q.get()
            url = item[0]
            path = LinkUtil.deconstruct_url(url)
            layer = item[1]
            print(f"Working on layer {layer}")

            links = Crawler.pull_processed_links(url)

            if len(links) > self.width:
                links = numpy.random.choice(list(links), self.width, replace=False)

            for link in links:
                print(f"Adding {link}")
                fulllink = Crawler.construct_url(self=self, link=link)
                Visualization.write_relationship_nx(g=graph, parent=path, child=link)

                if layer < self.depth:
                    q.put((fulllink, layer + 1))

        print("Success!")
        return graph


class BuildCrawler:

    def __init__(self,
                 create_key,
                 url: str = "https://en.wikipedia.org/wiki/Kraftwerk",
                 depth: int = 3,
                 width: int = 4
                 ):

        self._create_key = create_key
        self.url = url
        self.depth = depth
        self.width = width

    def with_url(self, url):
        """
        Inserts a url.
        """
        return BuildCrawler(
                    create_key = self._create_key,
                    url = url,
                    depth = self.depth,
                    width = self.width
                    ) 

    def with_depth(self, depth):
        """
        Inserts a depth value.
        """
        return BuildCrawler(
                    create_key = self._create_key,
                    url = self.url,
                    depth = depth,
                    width = self.width
                    ) 

    def with_width(self, width):
        """
        Inserts a url.
        """
        return BuildCrawler(
                    create_key = self._create_key,
                    url = self.url,
                    depth = self.depth,
                    width = width
                    ) 

    def to_crawler(self):
        """
        Create a Crawler object from the builder
        """
        return Crawler(
            create_key=self._create_key,
            url=self.url,
            depth=self.depth,
            width=self.width
            )


class Visualization:

    @staticmethod
    def establish_graph_graphviz(crawler):
        '''
        Initializes a graphviz strict digraph.
        :return: the graph object.
        '''

        g = Digraph('G',
                    filename=f"network_graphs/{crawler.url.replace('/', '_').replace(':', '_')}_network",
                    engine='sfdp',
                    format='png',
                    node_attr={
                        'color': 'blue',
                        'shape': 'circle',
                        },
                    strict=True
                    )

        return g

    @staticmethod
    def establish_graph_nx():
        '''
        Initializes a nx/plt graph
        :return: the graph object.
        '''

        g = nx.Graph()
        return g

    @staticmethod
    def write_relationship_graphviz(g, parent, child):
        '''
        Creates a graph relationship in graphviz between a parent and a child node. (Creates each as a node
        if they don't already exist.
        '''

        # pvalue = hash(parent)
        # cvalue = hash(child)

        # g.node(int(pvalue), label=str(parent))
        # g.node(int(cvalue), label=str(child))

        strippedparent = LinkUtil.remove_wiki_from_path(parent)
        strippedchild = LinkUtil.remove_wiki_from_path(child)

        g.edge(f"{strippedparent}", f"{strippedchild}")

    @staticmethod
    def write_relationship_nx(g, parent, child):
        '''
        Creates a graph relationship in networkx between a parent and a child node. (Creates each as a node
        if they don't already exist.
        '''
        strippedparent = LinkUtil.remove_wiki_from_path(parent)
        strippedchild = LinkUtil.remove_wiki_from_path(child)

        g.add_node(strippedparent)
        g.add_node(strippedchild)

        g.add_edge(strippedparent, strippedchild)

    @staticmethod
    def view_with_plt(g):
        '''
        Opens the nx/plt graph.
        '''

        nx.draw(g, with_labels=True)
        plt.show()

    @staticmethod
    def view_with_graphviz(crawler, g):
        '''
        Opens the graphviz file
        '''

        g.render(f"network_graphs/{crawler.url.replace('/', '_').replace(':', '_')}_network", view=True)
