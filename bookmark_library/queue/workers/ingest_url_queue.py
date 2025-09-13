"""This module contains the queue name and callback function
"""

import logging
import aio_pika

from bookmark_library.library_db.db_actions import create_record
from bookmark_library.queue.queue_names import SUMMARIZE_URL_QUEUE_NAME, INGEST_URL_QUEUE_NAME
from bookmark_library.queue.rabbitmq import publish_message

# Configure logging
logger = logging.getLogger(__name__)


async def bookmark_manager_ingest_url_callback(message: aio_pika.IncomingMessage):
    """Callback function for the queue

    This function will be called when a message is received from the queue."""
    try:
        url = message.body.decode()
        logger.info(f"Ingest received: {url}")

        try:
            # Create record in database
            logger.debug(f"Creating record for {url}")
            create_record(url)

            # Send to summarize queue
            logger.debug(f"Sending {url} to summarize queue")
            publish_message(url, SUMMARIZE_URL_QUEUE_NAME)

            logger.info(f"Successfully processed ingest for {url}")
        except Exception as processing_error:
            logger.error(f"Error processing URL {url}: {processing_error}")
            raise  # Re-raise to be caught by outer try/except

        # Acknowledge message
        await message.ack()
        logger.debug(f"Message for {url} acknowledged")

    except Exception as e:
        logger.error(f"Error in ingest callback for {message.body.decode() if message.body else 'unknown'}: {e}")
        # Reject message and send to dead letter queue
        await message.reject(requeue=False)
        logger.info(f"Message rejected and sent to dead letter queue")


def get_bookmark_manager_ingest_url_queue() -> tuple[str, callable]:
    """Get the queue name and callback function

    This function will return the queue name and callback function."""
    return INGEST_URL_QUEUE_NAME, bookmark_manager_ingest_url_callback
