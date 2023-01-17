import re

from pdfminer.high_level import extract_text_to_fp
from pdfminer.pdfdocument import PDFEncryptionError
from pdfminer.pdfparser import PDFSyntaxError

from record_convert import db_record_to_url_record, url_record_to_db_record
from selenium_download import get_html_selenium

print("Loading NLP tools and database...")

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from transformers import pipeline
print("Loading other tools...")

import psycopg2
import requests
from io import StringIO
from pdfminer.layout import LAParams
import pika, sys, os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

BOOKMARK_INGEST_QUEUE_NAME = 'bookmark_ingest'
BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME = 'bookmark_update_summary'

database = psycopg2.connect(DATABASE_URL)

summarization = pipeline("summarization")

print("NLP tools loaded")

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def get_all_urls():
    cursor = database.cursor()
    cursor.execute("SELECT id, created_at, url, title, summary FROM url")
    records = cursor.fetchall()
    print(f"Fetched {len(records)} records")
    return [db_record_to_url_record(r) for r in records]


def get_url(url):
    cursor = database.cursor()
    cursor.execute("SELECT id, created_at, url, title, summary FROM url WHERE url = %s", [str(url)])
    records = cursor.fetchall()
    record = records[0] if len(records) > 0 else None
    if record is not None:
        print(f"Fetched {len(record)} records")
        return db_record_to_url_record(record)
    else:
        print(f"Couldn't find {url}")
        return None


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
        if (url.startswith('https://twitter.com') or url.startswith("https://mobile.twitter.com")):
            return get_html_selenium(url)
        if (url[-4:] == ".pdf"):
            return download_pdf_url(url)
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
    ):
        print(f"Couldn't fetch {url}")
        filename = "errors.txt"
        with open(filename, 'a') as f:
            f.write(f"{url}\n")
        return ''


def wipe_ingest_file():
    filename = "ingest.txt"
    with open(filename, 'w') as f:
        print(f"Wiped Ingest File")
        f.write("")


def update_record(url):
    if url["dirty"]:
        db_record = url_record_to_db_record(url)
        cursor = database.cursor()
        if db_record[4] is not None or db_record[5] is not None:
            cursor.execute("UPDATE url SET title = %s, text = %s, html = %s, summary = %s WHERE id = %s", [db_record[3], db_record[4], db_record[5], db_record[6], db_record[0]])
        else:
            cursor.execute("UPDATE url SET title = %s, summary = %s WHERE id = %s", [db_record[3], db_record[6], db_record[0]])
        database.commit()
        print(f"Updated: {url['url']}")


def create_record(url):
    cursor = database.cursor()
    cursor.execute("INSERT INTO url (id, created_at, url, title, text, html) VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s)", [url, None, None, None])
    database.commit()
    print(f"Created: {url}")


def get_summary(text):
    # https://www.thepythoncode.com/article/text-summarization-using-huggingface-transformers-python
    try:
        if len(text) >= 1024:
            text = text[:1024]
        summary = summarization(text, )[0]['summary_text']
        return summary
    except:
        return "Error occurred in summarization"


def create_new_urls(urls):
    for url in urls:
        create_record(url)


def fill_in_missing_fields(urls):
    for url in urls:
        html = ""
        if not url["title"]:
            print(f"Fetched {url}")
            html = fetch_url(url["url"])
            url["dirty"] = True
            url["html"] = html
            url["title"] = get_title_from_html(html)
            url["text"] = get_text_from_html(html)


def fill_in_summary_field(urls):
    for url in urls:
        if url["summary"] is None:
            html = fetch_url(url["url"])
            text = get_text_from_html(html)
            summary = get_summary(text)
            url["summary"] = summary
            print(f"Summarized {url['url']}: {summary}")
            url["dirty"] = True


def download_pdf_url(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    }
    html = requests.get(url, headers=headers, timeout=10).content
    with open('temp.pdf', 'wb') as f:
        f.write(html)
    output_string = StringIO()
    with open('temp.pdf', 'rb') as f:
        try:
            extract_text_to_fp(f, output_string, laparams=LAParams(), output_type='html', codec=None);
        except (
            PDFSyntaxError, PDFEncryptionError
        ):
            print('Could not read this pdf')
    return output_string.getvalue().strip()


def main():
    credentials = pika.credentials.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD, erase_on_connect=False)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL, port=RABBITMQ_PORT, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue=BOOKMARK_INGEST_QUEUE_NAME)
    channel.queue_declare(queue=BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME)

    def ingest_callback(ch, method, properties, body):
        url_str = body.decode('utf-8')
        try:
            create_record(url_str)
            channel.basic_publish(exchange='', routing_key=BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME, body=body)
        except Exception as e:
            channel.basic_publish(exchange='', routing_key=BOOKMARK_INGEST_QUEUE_NAME, body=body)
            print( f'Error occurred with Ingest: {str(body)} {e}')
            raise f'Error occurred with Ingest'

        print(" [x] Received ingest %r" % url_str)

    def update_summary_callback(ch, method, properties, body):
        try:
            url_str = body.decode('utf-8')
            url = get_url(url_str)
            if url is None:
                # raise "An error occurred, filling info on non existing url"

                print(f'{url_str} not found. Creating.')
                channel.basic_publish(exchange='', routing_key=BOOKMARK_INGEST_QUEUE_NAME, body=body)
            else:
                fill_in_missing_fields([url])
                update_record(url)
                fill_in_summary_field([url])
                update_record(url)
                print('Updated Summary info for ', url_str)
        except Exception as e:
            channel.basic_publish(exchange='', routing_key=BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME, body=body)
            print(f'Error with Update Summary: {url_str} {e}')
            raise f'Error occurred with Update Summary'

        # fill_in_summary_field([body])
        # update_record(body)
        print(" [x] Received update record %r" % url_str)

    channel.basic_consume(queue=BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME, on_message_callback=update_summary_callback, auto_ack=True)
    channel.basic_consume(queue=BOOKMARK_INGEST_QUEUE_NAME, on_message_callback=ingest_callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
