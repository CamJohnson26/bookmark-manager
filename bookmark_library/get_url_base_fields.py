from bookmark_library.page_crawler.fetch_url import fetch_url
from bookmark_library.page_parser.get_text_from_html import get_text_from_html
from bookmark_library.page_parser.get_title_from_html import get_title_from_html


def get_url_base_fields(urls):
    for url in urls:
        html = ""
        if not url["title"]:
            print(f"Fetched {url}")
            html = fetch_url(url["url"])
            url["dirty"] = True
            url["html"] = html
            url["title"] = get_title_from_html(html)
            url["text"] = get_text_from_html(html)
    return urls
