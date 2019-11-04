import requests
from urllib.parse import urlparse


class LinkUtil:
    '''
    Link Utility class to vet links on wikipidea pages.
    All methods take a url as a string.
    '''

    @staticmethod
    def is_anchor(link):

        # Checks whether the link is an anchor link.
        if len(link) > 0 and link[0] == '#':
            return True
        else:
            return False

    @staticmethod
    def is_wiki_link(link):

        # Checks that the the link is internal to wikipedia.
        return len(link) > 0 and link[0:6] == '/wiki/'

    @staticmethod
    def is_wiki_special_type(link):

        # Checks for special page types in wikipedia.
        return len(link) > 0 and (link[6:15] == 'Category:'
                                  or link[6:14] == 'Special:'
                                  or link[6:11] == 'Talk:'
                                  or link[6:11] == 'Help:'
                                  or link[6:11] == 'File:'
                                  or link[6:15] == 'Wikipedia'
                                  or link[6:12] == 'Portal'
                                  )

    @staticmethod
    def is_image(link):

        # Checks for image file types.
        return len(link) > 0 and (link[:-4] == '.png'
                                  or link[:-4] == '.jpg'
                                  or link[:-5] == '.jpeg'
                                  )

    @staticmethod
    def is_active_link(link):

        # Checks that the link returns a status code in the 200 range.
        r = requests.get(link)
        return 199 < r.status_code < 300

    @staticmethod
    def is_html_link(link):

        # Checks that the link returns an html type.
        r = requests.get(link)
        h = r.headers['Content-Type']
        return h[0:9] == 'text/html'

    @staticmethod
    def deconstruct_url(url):

        # Deconstructs the URL and returns only the URL path as a string.
        parsedurl = urlparse(url)
        return parsedurl[2]

    @staticmethod
    def remove_wiki_from_path(path):

        # Removes the leading /wiki/ route from the internal wikipedia path.
        if "/wiki/" in path:
            path = path[6:]
        return path
