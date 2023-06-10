import asyncio
from threading import Thread

from ingest_url_queue import get_bookmark_manager_ingest_url_queue
from summarize_url_queue import get_bookmark_manager_summarize_url_queue
from rabbitmq import setup_rabbitmq


def initiate_background_tasks():
    """Initiate the background tasks."""
    try:
        loop = asyncio.new_event_loop()
        start_background_thread(loop)
        queues = [get_bookmark_manager_ingest_url_queue(), get_bookmark_manager_summarize_url_queue()]
        # Schedule the RabbitMQ setup function to run in the event loop
        asyncio.run_coroutine_threadsafe(setup_rabbitmq(loop, queues), loop)
    except Exception as e:
        print("Error:", e)


def start_background_thread(loop: asyncio.AbstractEventLoop):
    """Get the event loop"""
    t = Thread(target=loop.run_forever, daemon=True)
    t.start()


if __name__ == '__main__':
    """Main function to run the script

    This function will run the script and initiate the background tasks."""
    initiate_background_tasks()
