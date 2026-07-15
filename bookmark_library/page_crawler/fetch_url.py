from urllib.parse import urlparse

from bookmark_library.page_crawler.fetch_pdf_url import fetch_pdf_url
from bookmark_library.page_crawler.fetch_url_selenium import fetch_url_selenium


def fetch_url(url):
    if urlparse(url).path.lower().endswith(".pdf"):
        return fetch_pdf_url(url)

    return fetch_url_selenium(url)
