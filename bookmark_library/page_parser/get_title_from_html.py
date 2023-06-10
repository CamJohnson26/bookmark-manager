from bs4 import BeautifulSoup


def get_title_from_html(html):
    soup = BeautifulSoup(html, features="lxml")

    if soup.title is not None:
        return soup.title.get_text()
    else:
        return "No title found"
