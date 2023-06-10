"""This module contains the queue name and callback function
"""

import aio_pika

INGEST_URL_QUEUE_NAME = 'bookmark_manager_ingest_url'


async def bookmark_manager_ingest_url_callback(message: aio_pika.IncomingMessage):
    """Callback function for the queue

    This function will be called when a message is received from the queue."""
    try:
        print(f" [x] Received {message.body.decode()}")
        print('Ingest')
        await message.ack()
    except Exception as e:
        print("Error:", e)
        await message.reject(requeue=False)


def get_bookmark_manager_ingest_url_queue() -> tuple[str, callable]:
    """Get the queue name and callback function

    This function will return the queue name and callback function."""
    return INGEST_URL_QUEUE_NAME, bookmark_manager_ingest_url_callback
