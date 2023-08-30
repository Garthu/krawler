from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver import Chrome
from time import sleep

import csv
import re

def if_empty_set_none(string):
	if string == '':
		return 'None'
	else:
		return string


def init_csv(theme):
	data = ["title","date", "doi", "citations"]
	path = theme + '.csv'
	with open(path, 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(data)

def append_csv(data, theme):
	path = theme + '.csv'
	with open(path, 'a', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(data)

def get_page(driver, url):
	driver.get(url)

def get_links(driver):
	links = set()
	soup = BeautifulSoup(driver.page_source, 'lxml')

	for link in soup.find_all("h3"):
		children = link.findChildren("a", recursive=False)
		for child in children:
			soup_temp = BeautifulSoup(str(child), 'lxml')
			a_href = soup_temp.find("a").get("href")
			links.add(a_href)

	return links

def get_title(soup):
	try:
		title = soup.find("h1", {"class": "document-title text-2xl-md-lh"}).findChild().string
	except:
		title = ''

	return if_empty_set_none(title)

def get_date(soup):
	try:
		date = ''
		date_citation = soup.find("div", {"class": "u-pb-1 doc-abstract-dateadded"})
		date_pub = soup.find("div", {"class": "u-pb-1 doc-abstract-pubdate"})
		if date_citation != None:
			value = re.search("(?:January|February|March|April|May|June|July|August|September|October|November|December)[\s-]\d{4}", str(date_citation))
			data = value.group(0)
		if date_pub != None:
			value = re.search("(?:January|February|March|April|May|June|July|August|September|October|November|December)[\s-]\d{4}", str(date_pub))
			data = value.group(0)
	except Exception as ex:
		print(ex)
		date = ''

	return if_empty_set_none(date)

def get_doi(soup):
	try:
		doi = soup.find("div", {"class": "u-pb-1 stats-document-abstract-doi"}).findChild("a", recursive=False).string
	except:
		doi = ''

	return if_empty_set_none(doi)

def get_citation_number(soup):
	citation = ''
	try:
		for c in soup.find_all("button", {"class": "document-banner-metric text-base-md-lh col"}):
			if "Citations" in str(c) and "Paper" in str(c):
				citation = c.find("div").string
	except Exception as ex:
		print(ex)
		citation = ''

	return if_empty_set_none(citation)

def get_data(driver, links):
	url = 'https://ieeexplore.ieee.org'
	data = []

	for link in links:
		sleep(1)
		
		driver.get(url+link)
		soup = BeautifulSoup(driver.page_source, 'lxml')
		
		data.append(
			[get_title(soup),
			get_date(soup),
			get_doi(soup),
			get_citation_number(soup)]
		)

	return data


if __name__ == "__main__":
	driver = webdriver.Chrome(ChromeDriverManager().install())

	base_url = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText='
	search_word = 'security'
	number = 1

	init_csv(search_word)

	while(True):
		final_url = f'{base_url}{search_word}&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&pageNumber={number}'

		get_page(driver, final_url)
	
		links = get_links(driver)
	
		data = get_data(driver, links)
	
		append_csv(data, search_word)

		number += 1
