import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scraping.scraper import (
    fetch_static_data,
    fetch_dynamic_data,
    fetch_external_data,
)
from unittest.mock import patch, Mock
import pandas as pd


def test_fetch_static_data():
    html = "<html><head><title>Test</title></head><body><p>One</p><p>Two</p></body></html>"
    mock_resp = Mock(text=html, status_code=200)
    with patch('scraping.scraper.requests.get', return_value=mock_resp):
        df = fetch_static_data('http://dummy')
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 2
    assert set(df.columns) == {"title", "paragraph"}


def test_fetch_dynamic_data():
    html = "<html><head><title>Dyn</title></head><body><p>A</p></body></html>"
    mock_page = Mock(content=Mock(return_value=html))
    mock_browser = Mock(new_page=Mock(return_value=mock_page), close=Mock())
    # Using context manager patch for sync_playwright
    with patch('scraping.scraper.sync_playwright') as sp:
        sp.return_value.__enter__.return_value = Mock(firefox=Mock(launch=Mock(return_value=mock_browser)))
        df = fetch_dynamic_data('http://dummy')
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 1


def test_fetch_external_data():
    html = (
        "<table><tr><th>A</th><th>B</th></tr>"
        "<tr><td>1</td><td>2</td></tr></table>"
    )
    mock_resp = Mock(text=html, status_code=200)
    with patch("scraping.scraper.requests.get", return_value=mock_resp):
        df = fetch_external_data("http://dummy")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["A", "B"]
    assert df.iloc[0, 0] == "1"
