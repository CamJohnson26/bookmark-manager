import requests

from bookmark_library.page_crawler.fetch_pdf_url import fetch_pdf_url
from bookmark_library.page_crawler.fetch_url_selenium import fetch_url_selenium


def fetch_url(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    }
    try:
        if (url.startswith('https://twitter.com') or url.startswith("https://mobile.twitter.com")):
            return fetch_url_selenium(url)
        if (url[-4:] == ".pdf"):
            return fetch_pdf_url(url)
        else:
            html = requests.get(url, headers=headers, timeout=10)

            # Fixes this bug: https://stackoverflow.com/questions/57371164/django-postgres-a-string-literal-cannot-contain-nul-0x00-characters
            html = html.text.replace('\x00', '')

            return html
    except (
        requests.HTTPError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.SSLError,
        requests.exceptions.ConnectionError
    ) as e:
        print(f"Couldn't fetch {url}")
        raise Exception(f"Couldn't fetch {url}: {e}")
