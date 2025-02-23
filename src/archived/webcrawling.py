#!/usr/bin/python
# -*- coding: utf-8 -*-

from googlesearch import search
import requests
from bs4 import BeautifulSoup
import json
import pdb
from typing import List, Dict, Union
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from tqdm import tqdm


def remove_menu_elements(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Removes unnecessary navigation elements from the HTML to clean up the extracted text.
    :param soup: Parsed HTML content using BeautifulSoup
    :return: Cleaned BeautifulSoup object
    """
    # Remove navigation-related tags
    for tag in soup(['nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    # Remove elements by class
    menu_classes = ['nav', 'menu', 'navbar', 'sidebar', 'breadcrumb']
    for element in soup.find_all(class_=menu_classes):
        element.decompose()
    
    # Remove lists containing multiple links
    for ul in soup.find_all('ul'):
        if len(ul.find_all('a')) > 2:
            ul.decompose()
    
    return soup

def scrape_and_preprocess(url: str) -> Union[str, None]:
    """
    Fetches and processes webpage content, removing navigation elements and extracting meaningful text.
    :param url: URL of the webpage to scrape
    :return: Processed text content or an error message
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"
    
    # Adjust encoding for better text extraction
    if not response.encoding or response.encoding.lower() == 'iso-8859-1':
        response.encoding = response.apparent_encoding
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # pdb.set_trace()
    clean_soup = remove_menu_elements(soup)
    # pdb.set_trace()

    # Extract text from relevant tags
    text_lines: List[str] = []
    for element in clean_soup.find_all(['article']):
        if element.name == 'p' and not element.text.strip():
            continue  # Skip empty paragraphs
        text = element.get_text(separator=' ', strip=True)
        text_lines.append(text)
    
    # Merge paragraphs while filtering out very short ones
    processed_text = '\n\n'.join([line for line in text_lines])
    
    return processed_text

def web_search(query: str) -> List[Dict[str, str]]:
    """
    Performs a web search using Google Search API and scrapes the content of the top results.
    :param query: Search query string
    :return: A list of dictionaries containing link and extracted content
    """
    lst_responses = []
    response = search(query, sleep_interval=5, num_results=5, ssl_verify=False)
    
    for result in response:
        content = scrape_and_preprocess(result)
        lst_responses.append({'link': result, 'content': content})
    
    return lst_responses

def dynamic_web_page_scrape(url:str):
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open a dynamic webpage
    driver.get(url)

    # Wait for JavaScript to load (adjust time as needed)
    time.sleep(5)

    # Get the page source after JavaScript execution
    html = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Example: Extract all paragraph texts
    for p in soup.find_all("article"):
        print(p.text)

    # Close the browser
    driver.quit()
    pdb.set_trace()


def save_to_jsonl(obj, filename):
    """Save a list of dictionaries to a JSONL file."""
    with open(filename, "a+", encoding="utf-8") as file:
        file.write(json.dumps(obj, ensure_ascii=False) + "\n")


'''
Step1: Get links
'''
def get_targetted_links() -> None:
    # from 2024 June to 2025 Feb
    # Set up Selenium WebDriver
    """
    Batch processing by fetching and processing strait times financial crim from 2024 June to 2025 Feb.
    Looking out for "article" tab and store the content for offline processing.
    Due to dyanmic page loading, needs to wait for a few seconds in order for javascript to render the content.
    """
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    domain_url = 'https://www.straitstimes.com'
    base_url = 'https://www.straitstimes.com/tags/financial-crimes?page={page_number}'
    

    for page_number in range(0, 100):
        print(page_number)
        url = base_url.format(page_number=page_number)
        driver.get(url)
        time.sleep(10)
         # Get the page source after JavaScript execution
        html = driver.page_source

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a', class_='flex')
        lst_links = [link['href'] for link in links if link.has_attr('href')]

        with open('straittimes_financial_crimes.txt', 'a+') as file:
            for url in lst_links:
                print(f'{domain_url}{url}')
                file.write(f'{domain_url}{url}' + '\n')
    




    # for url in tqdm(links, total=len(links)):
       
    #     # Open a dynamic webpage
    #     driver.get(url)

    #     # Wait for JavaScript to load (adjust time as needed)
    #     time.sleep(5)

    #     # Get the page source after JavaScript execution
    #     html = driver.page_source

    #     # Parse with BeautifulSoup
    #     soup = BeautifulSoup(html, "html.parser")
    #     links = soup.find_all('a', class_='flex')
    #     lst_links = [link['href'] for link in links if link.has_attr('href')]

    #     with open('straittimes_financial_crimes.txt', 'a+') as file:
    #         for url in lst_links:
    #             file.write(f'{domain_url}{url}' + '\n')
    
    driver.quit()
    print('crawl finished.')


'''
Step2: Crawl link content
'''
def scraping_targetted_links() -> None:
    # from 2024 June to 2025 Feb
    # Set up Selenium WebDriver
    """
    Batch processing by fetching and processing strait times financial crim from 2024 June to 2025 Feb.
    Looking out for "article" tab and store the content for offline processing.
    Due to dyanmic page loading, needs to wait for a few seconds in order for javascript to render the content.
    """
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # file = open('../data/raw/output1.json', "w", encoding="utf-8")

    links = open('../data/raw/straittimes_financial_crimes.txt', 'r').readlines()

    for idx, url in enumerate(tqdm(links, total=len(links))):
        # if idx < 148: continue
        url = url.strip()
        # Open a dynamic webpage
        driver.get(url)

        # Wait for JavaScript to load (adjust time as needed)
        time.sleep(10)

        # Get the page source after JavaScript execution
        html = driver.page_source
        pdb.set_trace()
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # get article content
        article = soup.find("article")
        content = article.text
        # Example: Extract all paragraph texts
        # pdb.set_trace()
        # for p in soup.find_all("article"):
        #     print(p.text)

        # Close the browser
        print({'link': url, 'content': content})
        # output.append({'link': url, 'content': content})
        # pdb.set_trace()
        # save_to_jsonl({'link': url, 'content': content}, '../data/raw/output1.json')
        # file.write(json.dumps({'link': url, 'content': content}, ensure_ascii=False) + "\n")
        # content = dynamic_web_page_scrape(url)
        # print(content)
        # pdb.set_trace()
    # json.dump(output, open('../data/raw/output1.json', 'w'), indent=4)
    driver.quit()
    print('crawl finished.')




if __name__ == "__main__":
    # Example usage
    # responses = web_search(query='Saiful Alam Masud AND Bangladesh AND site:bloomberg.com OR site:straitstimes.com')
    # json.dump(responses, open('test_saiful.json', 'w'), indent=4)
    
    # test = json.load(open('test_saiful.json', 'r'))
    # print(test)
    # scraping_targetted_links()
    # get_targetted_links()
    # step 2
    scraping_targetted_links()
    
    linkset = set()

    with open('../data/raw/output1.json', 'r') as file:
        obj = json.loads(file.readline().strip())
        line = obj['link']
        content = obj['content']
        if line not in linkset:
            linkset.add(line)
        else:

            pdb.set_trace()




