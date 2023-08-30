import csv
import re
from typing import List, Set

from bs4 import BeautifulSoup

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver import Chrome

from time import sleep

from .crawler import Crawler

from article import Article, Author, Metric

BASE_URL = 'https://www.researchgate.net'

class ResearchGateCrawler(Crawler):
    def __init__(self, searchTerm: str):
        super().__init__(searchTerm)
        
        self.page = 0

        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def fetch(self, searchTerm: str, page: int) -> List[Article]:
        url = buildURL(searchTerm, page)

        self.driver.get(url)

        links = self.get_links()

        data = self.get_data(links)

        return data

    def getMore(self) -> List[Article]:
        self.page += 1

        return self.fetch(self.searchTerm, self.page)

    def get_links(self) -> Set[str]:
        return get_links(self.driver)
    
    def get_data(self, links) -> List[Article]:
        return get_data(self.driver, links)

    def shutdown(self):
        self.driver.close()

def buildURL(searchTerm: str, page: int) -> str:
    return f'{BASE_URL}/search/publication?q={searchTerm}&page={page}'

def if_empty_set_none(string):
	if string == '':
		return 'None'
	else:
		return string

def get_page(driver, url):
	driver.get(url)

def get_links(driver):
	links = set()
	soup = BeautifulSoup(driver.page_source, 'lxml')
	for link in soup.find_all("a", {"class": "nova-legacy-e-link nova-legacy-e-link--color-inherit nova-legacy-e-link--theme-bare"}):
		temp = link.get('href')
		if temp.startswith('publication'):
			links.add(temp)

	return links

def get_title(soup):
	try:
		title = soup.find("h1", {"class": "nova-legacy-e-text nova-legacy-e-text--size-xl nova-legacy-e-text--family-display nova-legacy-e-text--spacing-none nova-legacy-e-text--color-grey-900 research-detail-header-section__title"}).string
	except:
		title = ''

	return if_empty_set_none(title)

def get_date(li):
	try:
		value = re.search("(?:January|February|March|April|May|June|July|August|September|October|November|December)[\s-]\d{4}", li)
		date = value.group(0)
	except:
		date = ''

	return if_empty_set_none(date)

def get_doi(li):
	try:
		value = re.search('(10.(\d)+/([^(\s\>\"\<)])+)', li)
		doi = value.group(0)
	except:
		doi = ''

	return if_empty_set_none(doi)

def get_citation_number(soup):
	try:
		base = soup.find_all("div", {"class": "nova-legacy-e-text nova-legacy-e-text--size-m nova-legacy-e-text--family-sans-serif nova-legacy-e-text--spacing-none nova-legacy-e-text--color-inherit nova-legacy-c-nav__item-label"})
		value = re.search('(Citations[\s-]\(\d{1,}\))', str(base))
		citation = re.sub('[^0-9]', '', value.group(0))
	except:
		citation = ''

	return if_empty_set_none(citation)

def get_authors(soup) -> List[str]:
	try:
		authors_names = []

		authors = soup.find_all("div", {"class": "nova-legacy-e-text nova-legacy-e-text--size-m nova-legacy-e-text--family-display nova-legacy-e-text--spacing-none nova-legacy-e-text--color-inherit nova-legacy-e-text--clamp nova-legacy-v-person-list-item__title"})

		for author in authors:
			author_name = author.find("a")
			authors_names.append(author_name.text)

		return authors_names
	except:
		return []

def get_data(driver, links) -> List[Article]:
	data = []

	for link in links:
		sleep(1)

		url = f'{BASE_URL}/{link}'

		driver.get(url)

		soup = BeautifulSoup(driver.page_source, 'lxml')

		li = str(soup.find("div", {"class": "research-detail-header-section__metadata"}))

		article = build_article(
			get_title(soup),
			get_doi(li),
			get_authors(soup),
			int(get_citation_number(soup))
		)

		data.append(article)

	return data

def build_article(title: str, DOI: str, authors: List[str], citations: int) -> Article:
    authors = [Author(name) for name in authors]
    metrics = Metric(
		citations=citations
	)

    return Article(
        title=title,
        DOI=DOI,
        authors=authors,
        metrics=metrics
    )
