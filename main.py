import re

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import psycopg2
import requests

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
database = psycopg2.connect(DATABASE_URL)


def get_all_urls():
    cursor = database.cursor()
    cursor.execute("SELECT * FROM url")
    records = cursor.fetchall()
    return [db_record_to_url_record(r) for r in records]


def db_record_to_url_record(db_record):
    return {
        "id": db_record[0],
        "created_at": db_record[1],
        "url": db_record[2],
        "title": db_record[3],
        "text": db_record[4],
        "html": db_record[5]
    }


def get_text_from_html(html):
    soup = BeautifulSoup(html, features="lxml")
    text = soup.get_text().split('\n')
    text = '\n'.join(filter(lambda x: not re.match(r'^\s*$', x), text))
    return text


def fetch_url(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    }
    html = requests.get(url, headers=headers)
    return html.text


def crawl_urls(urls):
    for url in urls:
        print(get_text_from_html(fetch_url(url)))


def read_urls_from_file():
    filename = "ingest.txt"
    with open(filename) as f:
        lines = f.readlines()
    return [l.strip() for l in lines]


# print(read_urls_from_file())
urls = get_all_urls()
print(urls)
crawl_urls([u["url"] for u in urls])