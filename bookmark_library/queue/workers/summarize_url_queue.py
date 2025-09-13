"""This module contains the queue name and callback function
"""

import logging
import aio_pika

from bookmark_library.get_url_base_fields import get_url_base_fields
from bookmark_library.get_url_summary_fields import get_url_summary_fields
from bookmark_library.library_db.db_actions import get_url, update_record
from bookmark_library.queue.queue_names import INGEST_URL_QUEUE_NAME, SUMMARIZE_URL_QUEUE_NAME
from bookmark_library.queue.rabbitmq import publish_message

# Configure logging
logger = logging.getLogger(__name__)


async def bookmark_manager_summarize_url_callback(message: aio_pika.IncomingMessage):
    """Callback function for the queue

    This function will be called when a message is received from the queue."""
    try:
        url = message.body.decode()
        logger.info(f"Summarize received: {url}")

        # Get URL from database
        url_obj = get_url(url)

        if url_obj is None:
            # URL not found, send it to the ingest queue
            logger.info(f"URL '{url}' not found in database. Sending to ingest queue.")
            publish_message(url, INGEST_URL_QUEUE_NAME)
        else:
            # Process URL in two steps
            try:
                # Step 1: Get base fields
                logger.debug(f"Getting base fields for {url}")
                new_urls = get_url_base_fields([url_obj])
                url_obj = new_urls[0]
                update_record(url_obj)

                # Step 2: Get summary fields
                logger.debug(f"Getting summary fields for {url}")
                new_urls = get_url_summary_fields([url_obj])
                url_obj = new_urls[0]
                update_record(url_obj)

                logger.info(f"Successfully updated summary info for {url}")
            except Exception as processing_error:
                logger.error(f"Error processing URL {url}: {processing_error}")
                raise  # Re-raise to be caught by outer try/except

        # Acknowledge message
        await message.ack()
        logger.debug(f"Message for {url} acknowledged")

    except Exception as e:
        logger.error(f"Error in summarize callback for {message.body.decode() if message.body else 'unknown'}: {e}")
        # Reject message and send to dead letter queue
        await message.reject(requeue=False)
        logger.info(f"Message rejected and sent to dead letter queue")


def get_bookmark_manager_summarize_url_queue() -> tuple[str, callable]:
    """Get the queue name and callback function

    This function will return the queue name and callback function."""
    return SUMMARIZE_URL_QUEUE_NAME, bookmark_manager_summarize_url_callback
