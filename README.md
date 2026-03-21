# Ekantipur Scraper
**Audio Bee — Web Scraping Intern Practical Test**

A Playwright-based scraper that extracts entertainment news and the cartoon of the day from [ekantipur.com](https://ekantipur.com).

---

## Author
**Milan Paudel**
milanpaudel784@gmail.com

---

## What it does
- Scrapes top 5 articles from the Entertainment (मनोरञ्जन) section
- Scrapes the Cartoon of the Day from the cartoon page
- Saves everything to `output.json`

---

## Setup

```bash
# Install uv (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create and set up project
mkdir ekantipur-scraper
cd ekantipur-scraper
uv init
uv add playwright
uv run playwright install chromium
```

## Run

```bash
uv run python scraper.py
```

---

## Output format

```json
{
  "entertainment_news": [
    {
      "title": "Article headline",
      "image_url": "https://...",
      "category": "मनोरञ्जन",
      "author": "Author Name"
    }
  ],
  "cartoon_of_the_day": {
    "title": "Cartoon title",
    "image_url": "https://...",
    "author": "Cartoonist Name"
  }
}
```

---

## Files
| File | Description |
|---|---|
| `scraper.py` | Main scraper script |
| `output.json` | Extracted data |
| `pyproject.toml` | Project dependencies |
| `prompts.txt` | Prompts used during development |