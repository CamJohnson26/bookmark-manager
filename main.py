import re

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from transformers import pipeline

import os
import psycopg2
import requests

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
database = psycopg2.connect(DATABASE_URL)

summarization = pipeline("summarization")


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def get_all_urls():
    cursor = database.cursor()
    cursor.execute("SELECT * FROM url")
    records = cursor.fetchall()
    print(f"Fetched {len(records)} records")
    return [db_record_to_url_record(r) for r in records]


def db_record_to_url_record(db_record):
    return {
        "id": db_record[0],
        "created_at": db_record[1],
        "url": db_record[2],
        "title": db_record[3],
        "text": db_record[4],
        "html": db_record[5],
        "summary": db_record[6],
        "dirty": False
    }


def url_record_to_db_record(db_record):
    return [
        db_record["id"],
        db_record["created_at"],
        db_record["url"],
        db_record["title"],
        db_record["text"],
        db_record["html"],
        db_record["summary"],
    ]


def get_text_from_html(html):
    soup = BeautifulSoup(html, features="lxml")
    text = soup.get_text().split('\n')
    text = '\n'.join(filter(lambda x: not re.match(r'^\s*$', x), text))
    return text


def get_title_from_html(html):
    soup = BeautifulSoup(html, features="lxml")

    if (soup.title is not None):
        return soup.title.get_text()
    else:
        return "No title found"


def fetch_url(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    }
    try:
        html = requests.get(url, headers=headers, timeout=10)

        # Fixes this bug: https://stackoverflow.com/questions/57371164/django-postgres-a-string-literal-cannot-contain-nul-0x00-characters
        text = html.text.replace('\x00', '')

        return text
    except (requests.HTTPError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout, requests.exceptions.TooManyRedirects, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        print(f"Couldn't fetch {url}")
        return ''


def read_urls_from_file():
    filename = "ingest.txt"
    with open(filename) as f:
        lines = f.readlines()
    return [l.strip() for l in lines]


def wipe_ingest_file():
    filename = "ingest.txt"
    with open(filename, 'w') as f:
        print(f"Wiped Ingest File")
        f.write("")


def update_record(url):
    if url["dirty"]:
        db_record = url_record_to_db_record(url)
        cursor = database.cursor()
        cursor.execute("UPDATE url SET title = %s, text = %s, html = %s, summary = %s WHERE id = %s", [db_record[3], db_record[4], db_record[5], db_record[6], db_record[0]])
        database.commit()


def create_record(url):
    cursor = database.cursor()
    cursor.execute("INSERT INTO url (id, created_at, url, title, text, html) VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s)", [url, None, None, None])
    database.commit()
    print(f"Created: {url}")


def get_summary(text):
    # https://www.thepythoncode.com/article/text-summarization-using-huggingface-transformers-python
    if len(text) >= 1024:
        text = text[:1024]
    summary = summarization(text)[0]['summary_text']
    return summary


def create_new_urls(urls):
    for url in urls:
        create_record(url)


def fill_in_missing_fields(urls):
    for url in urls:
        html = ""
        if (not url["title"] or not url["text"] or not url["html"]):
            print(f"Fetched {url}")
            html = fetch_url(url["url"])
            url["dirty"] = True
        if (not url["html"]):
            url["html"] = html
        if (not url["title"]):
            url["title"] = get_title_from_html(html)
        if (not url["text"]):
            url["text"] = get_text_from_html(html)


def fill_in_summary_field(urls):
    for url in urls:
        text = url["text"]
        if url["summary"] is None and (text is not None):
            summary = get_summary(text)
            url["summary"] = summary
            print(f"Summarized {url['url']}: {summary}")
            url["dirty"] = True


ingest_urls = read_urls_from_file()

batches = list(batch(ingest_urls, 50))
index = 0

for batch in batches:
    create_new_urls(batch)

    urls = get_all_urls()
    fill_in_missing_fields(urls)

    for url in urls:
        update_record(url)
        print(f"Updated: {url}")

    fill_in_summary_field(urls)
    for url in urls:
        update_record(url)
        print(f"Updated: {url}")

    index += 1
    print(f"Batch {index} of {len(batches)} completed")

wipe_ingest_file()