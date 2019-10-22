import requests


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