import json
from playwright.sync_api import sync_playwright, TimeoutError

BASE_URL = "https://ekantipur.com"
OUTPUT_FILE = "output.json"  # output file location
TOP_N = 5  # getting top five news


def make_absolute(url):
    """
    Ensure the URL is absolute by checking its format.
    Handles relative paths (/) and protocol-relative URLs (//).
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
    Retrieve the value of the given attribute from the element.
    Returns None if the element is missing or the attribute doesn't exist.
    """
    try:
        return el.get_attribute(attr) if el else None
    except Exception:
        return None


def safe_goto(page, url) -> bool:
    """
    Navigate to a URL safely.
    Returns False on timeout or error instead of crashing the scraper.
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

    Navigates to the entertainment section and extracts up to TOP_N articles.
    Each article contains: title, image_url, author, category.

    Parameters:
        page: Playwright Page object

    Returns:
        list[dict]: List of article dicts, empty list if page fails to load.
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

    for card in cards[:TOP_N]:
        try:
            title = get_text(card.query_selector("h2 a"))

            img = card.query_selector("img")
            # data-src is used for lazy-loaded images; fall back to src
            image_url = make_absolute(
                get_attr(img, "data-src") or get_attr(img, "src")
            )

            author = get_text(card.query_selector(".author-name a"))

            # Category is always मनोरञ्जन on this page — no badge element exists
            article = {
                "title": title,
                "image_url": image_url,
                "author": author,
                "category": "मनोरञ्जन"
            }

            news_list.append(article)
            print(f"  + {title}")

        except Exception as e:
            print(f"  Skipping article: {e}")
            continue

    return news_list


def scrape_cartoon(page):
    """
    Scrape the Cartoon of the Day from Ekantipur.

    The description paragraph holds title and author together as "Title - Author".
    The full-resolution image URL is in the anchor href, not the img src.

    Parameters:
        page: Playwright Page object

    Returns:
        dict: {title, author, image_url}, or empty dict {} if scraping fails.
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
        # Description paragraph contains "Title - Author" as a single string
        text = get_text(page.query_selector(".cartoon-description p"))

        if text and " - " in text:
            title, author = text.split(" - ", 1)
        else:
            title, author = text, None

        # Prefer the anchor href (full resolution) over img src (thumbnail)
        link = page.query_selector(".cartoon-image a")
        image_url = make_absolute(get_attr(link, "href"))

        print(f"  + {title} by {author}")

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
    Orchestrates the full scrape and saves results to output.json.

    Launches a single Chromium browser, runs both scrapers on the same page,
    then writes the combined result to OUTPUT_FILE.

    Output format:
        {
            "entertainment_news": [ {title, image_url, author, category} ],
            "cartoon_of_the_day": {title, author, image_url}
        }
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
        "cartoon_of_the_day": cartoon
    }

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\nSaved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error saving file: {e}")


if __name__ == "__main__":
    run_scraper()