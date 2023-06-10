from bs4 import BeautifulSoup
import re


def get_text_from_html(html):
    soup = BeautifulSoup(html, features="lxml")
    text = soup.get_text().split('\n')
    text = '\n'.join(filter(lambda x: not re.match(r'^\s*$', x), text))
    return text
