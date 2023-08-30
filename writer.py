import csv
import json

from typing import List, Set

from base_logger import logger

from article import Article, Author
from util import fromDataclassesToDict

class Writer:
    def __init__(self, filePath: str):
        self.file = open(filePath, 'w')

    def write(self, articles: Set[Article]) -> bool:
        writableToFile = fromDataclassesToDict(articles)

        logger.debug('Writing parcial data to file')
        json.dump(writableToFile, self.file, ensure_ascii=False, indent=4)

        return True

    def close(self):
        self.file.close()

HEADERS = ['title', 'DOI', 'authors', 'citations']

class CSVWriter:
    def __init__(self, filePath: str):
        self.initWriter(filePath)

    def write(self, articles: Set[Article]) -> bool:
        writableToFile = [
            {
                'title': article.title,
                'DOI': article.DOI,
                'authors': format_authors_to_csv(article.authors),
                'citations': article.metrics.citations
            } 

            for article in articles
        ]

        self.writer.writerows(writableToFile)

        return True

    def initWriter(self, filePath: str):
        self.file = open(filePath, 'w', newline='')

        self.writer = csv.DictWriter(self.file, fieldnames=HEADERS)
        self.writer.writeheader()

    def close(self):
        self.file.close()

def format_authors_to_csv(authors: List[Author]) -> str:
    return '|'.join([author.name for author in authors])
