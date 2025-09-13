import asyncio
import logging
import signal
import time
import concurrent.futures
from threading import Event

from bookmark_library.queue.rabbitmq import setup_rabbitmq
from bookmark_library.queue.workers.ingest_url_queue import get_bookmark_manager_ingest_url_queue
from bookmark_library.queue.workers.summarize_url_queue import get_bookmark_manager_summarize_url_queue
from bookmark_library.background_jobs.healthcheck import get_healthcheck_task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for thread management
_executor = None
_stop_event = Event()
_loop = None
_future = None


def run_event_loop(loop: asyncio.AbstractEventLoop):
    """Run the event loop and handle exceptions"""
    global _stop_event

    asyncio.set_event_loop(loop)

    try:
        while not _stop_event.is_set():
            try:
                loop.run_forever()
            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                # Short sleep to prevent CPU spinning on repeated errors
                time.sleep(1)

                if not _stop_event.is_set():
                    logger.info("Restarting event loop")
                    # Create a new event loop if the old one is broken
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        # Re-initialize the queues and tasks
                        initialize_queues_and_tasks(loop)
    finally:
        try:
            # Cancel all running tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()

            # Run the event loop until all tasks are cancelled
            if not loop.is_closed():
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
        except Exception as e:
            logger.error(f"Error shutting down event loop: {e}")


def initialize_queues_and_tasks(loop: asyncio.AbstractEventLoop):
    """Initialize queues and tasks in the event loop"""
    try:
        # Set up queues
        queues = [
            get_bookmark_manager_ingest_url_queue(), 
            get_bookmark_manager_summarize_url_queue()
        ]

        # Schedule the RabbitMQ setup function to run in the event loop
        setup_task = asyncio.run_coroutine_threadsafe(setup_rabbitmq(queues), loop)

        # Schedule the periodic healthcheck task
        healthcheck_task = asyncio.run_coroutine_threadsafe(get_healthcheck_task(), loop)

        logger.info("Scheduled RabbitMQ setup and periodic healthcheck task")

        # Wait for setup to complete
        setup_task.result(timeout=30)
    except Exception as e:
        logger.error(f"Error initializing queues and tasks: {e}")
        raise


def start_background_thread(loop: asyncio.AbstractEventLoop):
    """Start a background thread to run the event loop using ThreadPoolExecutor"""
    global _executor, _loop, _stop_event, _future

    # Store the loop for later access
    _loop = loop

    # Reset stop event
    _stop_event.clear()

    # Create executor if it doesn't exist
    if _executor is None:
        _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="RabbitMQ-EventLoop")

    # Submit the task to the executor
    _future = _executor.submit(run_event_loop, loop)

    logger.info("Started background thread using ThreadPoolExecutor")

    # Register signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, shutdown_handler)


def shutdown_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    stop_background_tasks()


def stop_background_tasks():
    """Stop the background tasks and executor"""
    global _stop_event, _loop, _executor, _future

    if _stop_event.is_set():
        logger.info("Already shutting down")
        return

    logger.info("Stopping background tasks")
    _stop_event.set()

    if _loop and not _loop.is_closed():
        try:
            # Stop the event loop
            _loop.call_soon_threadsafe(_loop.stop)
        except Exception as e:
            logger.error(f"Error stopping event loop: {e}")

    # Wait for the future to complete
    if _future and not _future.done():
        try:
            # Wait for the future to complete with a timeout
            _future.result(timeout=5)
        except concurrent.futures.TimeoutError:
            logger.warning("Background thread did not terminate within timeout")
        except Exception as e:
            logger.error(f"Error waiting for background thread to terminate: {e}")

    # Shutdown the executor
    if _executor:
        _executor.shutdown(wait=False)
        _executor = None

    logger.info("Background tasks stopped")


def initiate_background_tasks():
    """Initiate the background tasks."""
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()

        # Start the background thread
        start_background_thread(loop)

        # Initialize queues and tasks
        initialize_queues_and_tasks(loop)

        logger.info("Background tasks initiated successfully")
    except Exception as e:
        logger.error(f"Error initiating background tasks: {e}")
        stop_background_tasks()
        raise


if __name__ == '__main__':
    """Main function to run the script

    This function will run the script and initiate the background tasks."""
    try:
        logger.info("Starting background job service")
        initiate_background_tasks()

        # Keep the main thread alive to allow the background thread to run
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, shutting down")
                break
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}")
    finally:
        # Ensure we always clean up
        stop_background_tasks()
        logger.info("Background job service stopped")
