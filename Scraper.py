import json
from playwright.sync_api import sync_playwright, TimeoutError

BASE_URL = "https://ekantipur.com"
OUTPUT_FILE = "output.json" #output file location
TOP_N = 5 #getting top five news


def make_absolute(url):
    """
    this function ensure thr base url is correct by doing some format checking
    
    """
    if not url:
        return None
    if url.startswith("/"):
        return BASE_URL + url
    if url.startswith("//"):
        return "https:" + url
    return url


def get_text(el):
    """ 
    Return cleaned text from an element, or None if unavailable.
    Handles missing elements and avoids crashes during scraping.
    
    """
    try:
        return el.inner_text().strip() if el else None
    except Exception:
        return None


def get_attr(el, attr):
    """
    This function attempts to retrieve the value of the given attribute from the element.
    If the element is None or an error occurs (e.g., attribute missing)
    it returns None instead of raising an exception.

    """
    try:
        return el.get_attribute(attr) if el else None
    except Exception:
        return None


def safe_goto(page, url) ->bool:
    """
    This function attempts to open the specified URL in the provided page object.
    If the page fails to load (timeout or other errors), it logs the issue and
    returns False instead of raising an exception.

    """
    try:
        print(f"Opening: {url}")
        page.goto(url, timeout=30000)
        return True
    except TimeoutError:
        print("Timeout while loading page")
        return False
    except Exception as e:
        print(f"Error opening page: {e}")
        return False
    
    
