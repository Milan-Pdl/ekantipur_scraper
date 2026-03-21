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

def scrape_entertainment(page):
    """
       Scrape the top entertainment articles from Ekantipur.

    This function navigates to the entertainment section of ekantipur.com
    and extracts a list of articles, each containing:
        - title
        - image URL
        - author
        - category (typically 'मनोरञ्जन' beacaue we are hiting entertainment endpoint)

    It handles:
        - Page navigation errors
        - Missing or malformed elements
        - Timeouts while waiting for articles

    Parameters:
        page: Playwright Page object
            The browser tab to perform scraping on.

    Returns:
        list[dict]:
            - Each dict contains:
                {
                    "title": str | None,
                    "image_url": str | None,
                    "author": str | None,
                    "category": str
                }
            - Returns an empty list if page fails to load or no articles found.

    Example usage:
        articles = scrape_entertainment(page)
        for article in articles:
            print(article["title"])
    

    """
    print("\nScraping entertainment news...")

    if not safe_goto(page, f"{BASE_URL}/entertainment"):
        return []

    try:
        page.wait_for_selector(".category-inner-wrapper", timeout=10000)
    except TimeoutError:
        print("No news cards found")
        return []

    cards = page.query_selector_all(".category-inner-wrapper")

    if not cards:
        print("No articles found")
        return []

    news_list = []

    for i, card in enumerate(cards[:TOP_N]):
        try:
            title = get_text(card.query_selector("h2 a"))

            img = card.query_selector("img")
            image_url = make_absolute(
                get_attr(img, "data-src") or get_attr(img, "src")
            )

            author = get_text(card.query_selector(".author-name a"))

            article = {
                "title": title,
                "image_url": image_url,
                "author": author,
                "category": "मनोरञ्जन"
            }

            news_list.append(article)

            print(f" + {title}")

        except Exception as e:
            print(f"Skipping one article due to error: {e}")
            continue

    return news_list

def scrape_cartoon(page):
    """
    Scrape the Cartoon of the Day from Ekantipur.

    This function navigates to the cartoon section of ekantipur.com and extracts:
        - title: The cartoon title
        - author: The cartoon author
        - image_url: The URL of the cartoon image

    The title and author are usually stored together in a paragraph
    as "Title - Author". The function splits this string to extract
    both fields.

    It handles:
        - Page navigation errors
        - Timeouts when waiting for cartoon elements
        - Missing or malformed elements
        - Parsing errors

    Parameters:
        page: Playwright Page object
            The browser tab used for scraping.

    Returns:
        dict:
            {
                "title": str | None,
                "author": str | None,
                "image_url": str | None
            }
            Returns an empty dict {} if scraping fails.

    Example usage:
        cartoon = scrape_cartoon(page)
        print(cartoon["title"], "by", cartoon["author"])
    """
    print("\nScraping cartoon...")

    if not safe_goto(page, f"{BASE_URL}/cartoon"):
        return {}

    try:
        page.wait_for_selector(".cartoon-image", timeout=10000)
    except TimeoutError:
        print("Cartoon not found")
        return {}

    try:
        text = get_text(page.query_selector(".cartoon-description p"))

        if text and " - " in text:
            title, author = text.split(" - ", 1)
        else:
            title, author = text, None

        link = page.query_selector(".cartoon-image a")
        image_url = make_absolute(get_attr(link, "href"))

        print(f" + {title} by {author}")

        return {
            "title": title,
            "author": author,
            "image_url": image_url
        }

    except Exception as e:
        print(f"Error extracting cartoon: {e}")
        return {}

def run_scraper():
    """
    Run the Ekantipur scraper and save results to a JSON file.

    This function:
        1. Launches a Playwright Chromium browser.
        2. Opens a page and scrapes:
            - Top entertainment articles (scrape_entertainment)
            - Cartoon of the Day (scrape_cartoon)
        3. Closes the browser safely.
        4. Saves the collected data to 'output.json'.
    
    Error handling:
        - Any browser or scraping error is caught and logged.
        - File write errors are caught and logged.
        - Function continues without crashing on individual errors.

    Parameters:
        None

    Returns:
        None
        - Output is written to 'output.json' in the current directory.

    Example usage:
        run_scraper()
        -> Saves entertainment news and cartoon to output.json
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            entertainment = scrape_entertainment(page)
            cartoon = scrape_cartoon(page)

            browser.close()

    except Exception as e:
        print(f"Critical error: {e}")
        return

    data = {
        "entertainment_news": entertainment,
        "cartoon": cartoon
    }

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("\nSaved to output.json ")

    except Exception as e:
        print(f"Error saving file: {e}")


if __name__ == "__main__":
    run_scraper()

