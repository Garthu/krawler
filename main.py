import signal

from crawler_manager import CrawlersManager
from crawlers import ACMCrawler, ResearchGateCrawler

from writer import CSVWriter

def signal_handler(signum, frame):
    print('\nGracefully exiting, bye bye.')

    global cm
    cm.shutdown()

signal.signal(signal.SIGINT, signal_handler)

crawlers = [ACMCrawler('RDMA'), ResearchGateCrawler('security')]
writer = CSVWriter('csvs/my.csv')

cm = CrawlersManager(crawlers, writer)

cm.start()

cm.join()
