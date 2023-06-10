"""This module contains the queue name and callback function
"""

import aio_pika

from bookmark_library.library_db.db_actions import create_record
from bookmark_library.queue.queue_names import SUMMARIZE_URL_QUEUE_NAME, INGEST_URL_QUEUE_NAME
from bookmark_library.queue.rabbitmq import publish_message


async def bookmark_manager_ingest_url_callback(message: aio_pika.IncomingMessage):
    """Callback function for the queue

    This function will be called when a message is received from the queue."""
    try:
        url = message.body.decode()
        print(f" [x] Ingest Received {url}")
        create_record(url)
        publish_message(url, SUMMARIZE_URL_QUEUE_NAME)
        await message.ack()
    except Exception as e:
        print("Error:", e)
        await message.reject(requeue=False)


def get_bookmark_manager_ingest_url_queue() -> tuple[str, callable]:
    """Get the queue name and callback function

    This function will return the queue name and callback function."""
    return INGEST_URL_QUEUE_NAME, bookmark_manager_ingest_url_callback
