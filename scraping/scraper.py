"""Web scraping utilities for MicroAnalytics."""
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import requests


def _parse_html(html: str) -> pd.DataFrame:
    """Return dataframe with page title and paragraph texts."""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else ""
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    return pd.DataFrame({"title": [title] * len(paragraphs), "paragraph": paragraphs})


def fetch_static_data(url: str) -> pd.DataFrame:
    """Download static content using requests."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return _parse_html(resp.text)


def fetch_dynamic_data(url: str) -> pd.DataFrame:
    """Render dynamic page via Playwright and parse the HTML."""
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
    return _parse_html(html)


def fetch_external_data(url: str) -> pd.DataFrame:
    """Download table data from an external webpage."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = [
        [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        for row in soup.find_all("tr")
    ]
    if not rows:
        return pd.DataFrame()
    header, *data = rows
    return pd.DataFrame(data, columns=header)


__all__ = ["fetch_static_data", "fetch_dynamic_data", "fetch_external_data"]
