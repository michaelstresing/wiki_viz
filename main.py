from wiki_crawl import Crawler, BuildCrawler
import argparse, os

def parse_input():

    # Setup
    parser = argparse.ArgumentParser(description='Interface to setup the crawler.')

    # Adds Depth
    parser.add_argument('--d', '--depth',
                        type=int,
                        help='Set number of layers of extraction away from the original link you\'d like the crawler to go.\
                            Note: slow downs may be caused by more than a few layers.',
                        default=3
                        )

    # Adds Width
    parser.add_argument('--w', '--width',
                        type=int,
                        help="Set the number of links (randomly selected) per page you'd like the crawler to add to add to\
                            the visualization.",
                        default=4
                        )

    # Adds URL start
    parser.add_argument('--url',
                        type=str,
                        help='Set the starting url for the crawler.',
                        default='https://en.wikipedia.org/wiki/Kraftwerk'
                        )

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    # Check env variable to allow for nx graphing.
    outputtype = os.environ.get("WIKI_CRAWL_OUTPUT")

    # Parse the CLI inputs
    targs = parse_input()

    print(targs)

    # Create a new Cralwer (using the Builder Method pattern)
    usr = Crawler.new()\
        .with_depth(targs.d)\
        .with_width(targs.w)\
        .with_url(targs.url)

    usr = usr.to_crawler()
    
    # Print user feedback
    print(f'Crawling {targs.w} links per page, {targs.d} layers deeps, starting with {targs.url}')

    # Execute Crawl (Default is Graphviz output, unless env variable = nx)
    if outputtype == 'nx':
        graph = usr.run_crawler_plt()
        Visualization.view_with_plt(g)
    else:
        usr.run_crawler_graphviz()