import requests
from typing import List, Dict

from bs4 import BeautifulSoup

from .crawler import Crawler

from article import Article, Author, Metric

BASE_URL = 'https://dl.acm.org/action/doSearch'

class ACMCrawler(Crawler):
    def __init__(self, searchTerm: str):
        super().__init__(searchTerm)

        # Little hack to just always use getMore()
        self.page = -1
        self.pageSize = 20
        self.html = ''

    def fetch(self, searchTerm: str, pageSize: int, page: int):
        url = buildURL(searchTerm, pageSize, page)

        response = requests.get(url, verify=False)

        if response.ok:
            return response.text

    def parse(self, html: str) -> List[Article]:
        soup = BeautifulSoup(html, 'html.parser')

        publicationCards = soup.find_all('div', class_='issue-item issue-item--search clearfix')

        return [
            buildArticle(
                getTitle(card),
                getDOI(card),
                getAuthors(card),
                getMetrics(card)
            )

            for card in publicationCards
        ]

    def getMore(self) -> List[Article]:
        self.page += 1

        response = self.fetch(self.searchTerm, self.pageSize, self.page)

        return self.parse(response)

    def shutdown(self):
        ...

def buildURL(searchTerm: str, pageSize: int, startPage: int):
    return f'{BASE_URL}?AllField={searchTerm}&pageSize={pageSize}&startPage={startPage}'

def getPublicationDate(tag):
    publicationDate = tag.find('div', class_='bookPubDate simple-tooltip__block--b')

    return publicationDate.get_text()

def getTitle(tag):
    try:
        title = tag.find('div', class_='issue-item__content-right')
        title = title.find('h5')
        title = title.find('span')
    
        return title.find('a').get_text()
    except:
        return ''

def getAuthors(tag) -> List[str]:
    try:
        authors = tag.find('div', class_='issue-item__content')
        authors = authors.find('ul')

        authorsList = []
        for li in authors.find_all('li'):
            authorName = li.find('a')['title']
            authorsList.append(authorName)

        return authorsList
    except:
        return []

def getMetrics(tag) -> Dict[str, str]:
    try:
        citations = tag.find('span', class_='citation').get_text()
        downloads = tag.find('span', class_='metric').get_text()

        return {
            'citations': citations,
            'downloads': downloads
        }
    except:
        return {
            'citations': '',
            'downloads': ''
        }

def getDOI(tag) -> str:
    try:
        return tag.find('a', class_='issue-item__doi dot-separator').get_text()
    except:
        return ''


def buildArticle(title: str, DOI: str, authors: List[str], metrics: Dict[str, str]) -> Article:
    authors = [Author(name) for name in authors]
    metrics = Metric(metrics['citations'], metrics['downloads'])

    return Article(
        title=title,
        DOI=DOI,
        authors=authors,
        metrics=metrics
    )
