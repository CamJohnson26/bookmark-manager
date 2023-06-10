"""This module contains the queue name and callback function
"""

import aio_pika

from bookmark_library.get_url_base_fields import get_url_base_fields
from bookmark_library.get_url_summary_fields import get_url_summary_fields
from bookmark_library.library_db.db_actions import get_url, update_record
from bookmark_library.queue.queue_names import INGEST_URL_QUEUE_NAME, SUMMARIZE_URL_QUEUE_NAME
from rabbitmq import publish_message



async def bookmark_manager_summarize_url_callback(message: aio_pika.IncomingMessage):
    """Callback function for the queue

    This function will be called when a message is received from the queue."""
    try:
        print(f" [x] Summarize Received {message.body.decode()}")
        url = message.body.decode()
        url_obj = get_url(url)
        if url_obj is None:
            # raise "An error occurred, filling info on non existing url"

            print(f'{url} not found. Creating it.')
            publish_message(INGEST_URL_QUEUE_NAME, url)
        else:
            new_urls = get_url_base_fields([url_obj])
            url_obj = new_urls[0]
            update_record(url_obj)
            new_urls = get_url_summary_fields([url_obj])
            url_obj = new_urls[0]
            update_record(url_obj)
            print('Updated Summary info for ', url)
        await message.ack()

    except Exception as e:
        print("Error:", e)
        await message.reject(requeue=False)


def get_bookmark_manager_summarize_url_queue() -> tuple[str, callable]:
    """Get the queue name and callback function

    This function will return the queue name and callback function."""
    return SUMMARIZE_URL_QUEUE_NAME, bookmark_manager_summarize_url_callback
