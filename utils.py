import sys
import requests
from bs4 import BeautifulSoup, Tag

def get_fandom_link(args):
    """Parses command-line arguments to find the fandom link."""
    for arg in args:
        if arg.startswith("link="):
            return arg.split("=", 1)[1]
    return input("Masukkan link halaman Fandom (misal: https://example.fandom.com/wiki/example): ").strip()

def fetch_page(url, is_intro=False):
    """Fetches a web page and returns a BeautifulSoup object."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        print(f"Successfully fetched content from: {url}")
        return BeautifulSoup(res.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        if is_intro:
            print(f"Warning: Could not fetch introduction content from {url}: {e}. Proceeding without separate intro content.")
            return None
        raise

def find_title(soup):
    """Finds the character name from the page title."""
    title_element = soup.find('h1', class_='page-header__title')
    return title_element.text.strip() if title_element else None

def is_stop_tag(tag):
    """Checks if a tag is a section boundary."""
    if isinstance(tag, Tag):
        if tag.name in ['h2', 'h1'] and tag.find('span', class_='mw-headline'):
            return True
        if tag.name == 'div' and tag.get('class') and 'mw-parser-output' in tag.get('class'):
            return True
        if tag.name == 'div' and tag.get('id') == 'toc':
            return True
    return False
