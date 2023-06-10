from bookmark_library.page_crawler.fetch_url import fetch_url
from bookmark_library.page_parser.get_summary import get_summary
from bookmark_library.page_parser.get_text_from_html import get_text_from_html


def get_url_summary_fields(urls):
    for url in urls:
        if url["summary"] is None:
            html = fetch_url(url["url"])
            text = get_text_from_html(html)
            summary = get_summary(text)
            url["summary"] = summary
            print(f"Summarized {url['url']}: {summary}")
            url["dirty"] = True
    return urls
