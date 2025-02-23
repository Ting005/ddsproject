#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Web scraper for financial crime articles from The Straits Times.
Uses Google Search, BeautifulSoup, and Selenium to scrape and process articles.
"""

from googlesearch import search
import requests
from bs4 import BeautifulSoup
import json
import pdb
from typing import List, Dict, Union
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm
import pdb


def clean_article(text: str) -> str:
    """
    Cleans the given article text by removing unrelated content such as disclaimers, promotions, and legal terms.
    :param text: Raw article text
    :return: Cleaned article text
    """
    # Define patterns to remove common unrelated content
    patterns_to_remove = [
        r'Catch up on the news that everyone’s talking about',
        r'Thank you!',
        r'Sign up',
        r'By signing up, I accept SPH Media.*?',
        r'Yes, I would also like to receive SPH Media Group.*?',
        r'For more information on scams, members of the public can visit.*?',
        r'Anyone with information on such scams may call.*?',
        r'Join ST\'s WhatsApp Channel and get the latest news and must-reads.*?',
        r'Money launderingSingapore crimeFinancial crimesCrimeThanks for sharing!' 
    ]
    
    # Remove defined patterns
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # Remove extra whitespace and blank lines
    text = re.sub(r'\n+', '\n', text).strip()
    
    return text


def remove_menu_elements(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Cleans up webpage HTML by removing navigation elements (menus, headers, etc.).
    :param soup: Parsed HTML (BeautifulSoup object)
    :return: Cleaned HTML content
    """
    # Remove unwanted sections
    for tag in soup(['nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    # Remove menu-related elements by class
    menu_classes = ['nav', 'menu', 'navbar', 'sidebar', 'breadcrumb']
    for element in soup.find_all(class_=menu_classes):
        element.decompose()
    
    # Remove large lists of links (common in menus)
    for ul in soup.find_all('ul'):
        if len(ul.find_all('a')) > 2:
            ul.decompose()
    
    return soup


def scrape_and_preprocess(url: str) -> Union[str, None]:
    """
    Fetches a webpage and extracts meaningful text while removing navigation elements.
    :param url: Webpage URL
    :return: Processed article text or error message
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
    
    # Fix encoding issues
    if not response.encoding or response.encoding.lower() == 'iso-8859-1':
        response.encoding = response.apparent_encoding
    
    soup = BeautifulSoup(response.text, 'html.parser')
    clean_soup = remove_menu_elements(soup)

    # Extract article content
    text_lines: List[str] = []
    for element in clean_soup.find_all('article'):
        text = element.get_text(separator=' ', strip=True)
        text_lines.append(text)
    
    return '\n\n'.join([line for line in text_lines])  # Filter short lines


def web_search(query: str) -> List[Dict[str, str]]:
    """
    Uses Google Search API to find relevant links and scrapes their content.
    :param query: Search query
    :return: List of {'link': URL, 'content': extracted text}
    """
    results = []
    search_results = search(query, sleep_interval=5, num_results=5, ssl_verify=False)
    
    for result in search_results:
        content = scrape_and_preprocess(result)
        results.append({'link': result, 'content': content})
    
    return results


def save_to_jsonl(obj, filename):
    """
    Saves a list of dictionaries to a JSONL (JSON Lines) file.
    :param obj: Data object (dictionary)
    :param filename: File path
    """
    with open(filename, "a+", encoding="utf-8") as file:
        file.write(json.dumps(obj, ensure_ascii=False) + "\n")


# -------------------------
# STEP 1: GET ARTICLE LINKS
# -------------------------

def get_targeted_links() -> None:
    """
    Extracts article links for financial crime news from The Straits Times (2024-2025).
    Uses Selenium for dynamic page loading.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    domain_url = 'https://www.straitstimes.com'
    base_url = 'https://www.straitstimes.com/tags/financial-crimes?page={page_number}'
    
    for page_number in range(0, 100):  # Adjust range as needed
        print(f"Fetching page {page_number}...")
        url = base_url.format(page_number=page_number)
        driver.get(url)
        time.sleep(10)  # Wait for JS rendering

        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.find_all('a', class_='flex')

        # Extract valid links
        lst_links = [link['href'] for link in links if link.has_attr('href')]

        with open('../data/raw/straittimes_financial_crimes.txt', 'a+') as file:
            for url in lst_links:
                full_url = f'{domain_url}{url}'
                print(full_url)
                file.write(full_url + '\n')

    driver.quit()
    print('Link extraction completed.')


# -------------------------
# STEP 2: SCRAPE ARTICLE CONTENT
# -------------------------

def dynamic_web_page_scrape_and_process(url: str) -> str:
    """
    Scrapes content from a given article URL using Selenium.
    
    :param url: The URL of the article to scrape.
    :return: Extracted article text (or error message if not found).
    """
    # Initialize Selenium WebDriver (headless for efficiency)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Load the webpage
        url = url.strip()
        # print(url)
        driver.get(url)
        time.sleep(10)  # Wait for JavaScript to load content

        # Parse the dynamically loaded page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Extract the article content
        article = soup.find("article")

        # Return extracted text if available
        return article.text.strip() if article else "Error: Article not found"
    
    except Exception as e:
        return f"Scraping failed: {str(e)}"

    finally:
        driver.quit()  # Ensure the driver is closed


# -------------------------
#  Testing
# -------------------------

if __name__ == "__main__":
    # Uncomment the functions to run the specific steps
    # Step 1: Collect links
    # get_targeted_links()
    
    # Step 2: Scrape article content
    # dynamic_web_page_scrape_and_process()

    # testing
    url = "https://www.straitstimes.com/asia/se-asia/philippines-welcomes-removal-from-money-laundering-grey-list"
    article_text = dynamic_web_page_scrape_and_process(url)
    print(article_text)

