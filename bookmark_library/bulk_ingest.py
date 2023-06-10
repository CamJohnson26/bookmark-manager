from bookmark_library.get_new_urls import get_new_urls
from bookmark_library.local_files.save_and_reset_ingest import save_and_reset_ingest
from bookmark_library.queue.queue_names import INGEST_URL_QUEUE_NAME
from bookmark_library.queue.rabbitmq import publish_message


def bulk_ingest():
    new_urls = get_new_urls()
    print(f"Found {len(new_urls)} new urls")
    print(new_urls)

    for url in new_urls:
        publish_message(url, INGEST_URL_QUEUE_NAME)
    save_and_reset_ingest()

