import threading
import time

from base_logger import logger

from internet import hasConnection

from writer import Writer

ARTICLES_THRESHOLD = 20


def batchSize(data):
    return len(data) >= ARTICLES_THRESHOLD

def printInfo(articles):
    print(articles)
    print(len(articles))
    print()

## Manages the crawlers and save results in a file
class CrawlersManager(threading.Thread):
    def __init__(self, crawlers, writer):
        super().__init__()

        self.shutdown_ = False

        self.crawlers = crawlers
        self.writer = writer

    def run(self):
        logger.info('Started CrawlerManager')

        articles = set()

        waitForConnection()

        while not self.shutdown_:
            for crawler in self.crawlers:
                logger.info('Fetching...')
                articles.update(crawler.getMore())

            printInfo(articles)

            if batchSize(articles):
                self.writer.write(articles)

                articles = set()

        self.shutdownCrawlers()
        self.writer.close()

    def shutdownCrawlers(self):
        logger.info('Shutting down crawlers...')
        for crawler in self.crawlers:
            crawler.shutdown()

    def shutdown(self):
        logger.info('Shutting down CrawlerManager')
        self.writer.close()

        self.shutdown_ = True


def waitForConnection():
    while not hasConnection():
        print('Trying to connect to the internet...')
        time.sleep(3)
