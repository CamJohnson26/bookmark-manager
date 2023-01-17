
import pika, os
from dotenv import load_dotenv
import psycopg2

from record_convert import db_record_to_url_record

HARD_UPDATE = False

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

BOOKMARK_INGEST_QUEUE_NAME = 'bookmark_ingest'
BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME = 'bookmark_update_summary'

database = psycopg2.connect(DATABASE_URL)


def get_all_urls():
    cursor = database.cursor()
    cursor.execute("SELECT id, created_at, url, title, summary FROM url")
    records = cursor.fetchall()
    print(f"Fetched {len(records)} records")
    return [db_record_to_url_record(r) for r in records]


def deduplicate_ingest_file():
    filename = "ingest.txt"
    with open(filename) as f:
        lines = f.readlines()
    found = {}
    duplicates = {}
    lines = [l.strip() for l in lines]
    new_file = ""
    for line in lines:
        if not found.get(line) is True:
            found[line] = True
            new_file += f"{line}\n"
        else:
            duplicates[line] = 1 + duplicates.get(line, 0)
    print(f"Removed {len(duplicates.keys())} duplicate urls")
    for key in duplicates.keys():
        print(f"{duplicates[key]} instances of {key}")
    with open(filename, 'w') as f:
        print("Rewrote ingest file")
        f.write(new_file[:-1])


def read_urls_from_file():
    filename = "ingest.txt"
    with open(filename) as f:
        lines = f.readlines()
    return [l.strip() for l in lines]


def get_new_urls():
    deduplicate_ingest_file()
    ingest_urls = read_urls_from_file()

    existing_urls = [url["url"] for url in get_all_urls()]
    new_urls = [url for url in ingest_urls if url not in existing_urls]

    return new_urls


if __name__ == '__main__':
    new_urls = get_new_urls()
    all_urls = [url["url"] for url in get_all_urls()]

    credentials = pika.credentials.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD, erase_on_connect=False)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_URL, port=RABBITMQ_PORT, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue=BOOKMARK_INGEST_QUEUE_NAME)
    channel.queue_declare(queue=BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME)

    for url in new_urls:
        channel.basic_publish(exchange='', routing_key=BOOKMARK_INGEST_QUEUE_NAME, body=url)
        print(f" [x] Sent New: '{url}'")

    if HARD_UPDATE:
        for url in all_urls:
            channel.basic_publish(exchange='', routing_key=BOOKMARK_UPDATE_SUMMARY_QUEUE_NAME, body=url)
            print(f" [x] Sent Update: '{url}'")

    if len(new_urls) == 0:
        print('Found no new urls')
    connection.close()
