import sys
import logging
import asyncio
import time
import aio_pika
import pika
from dotenv import load_dotenv
import os
from functools import wraps
from typing import Optional, Callable, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
token = os.environ.get("api-token")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

# Global connection pool
_connection_pool = None
_channel_pool = None
_max_retries = 3
_retry_delay = 1  # seconds


def with_connection_retry(func: Callable) -> Callable:
    """Decorator to retry a function with connection handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        last_exception = None

        while retries < _max_retries:
            try:
                return func(*args, **kwargs)
            except (pika.exceptions.AMQPConnectionError, 
                    pika.exceptions.ChannelClosedByBroker,
                    pika.exceptions.ConnectionClosedByBroker) as e:
                last_exception = e
                retries += 1
                logger.warning(f"Connection error: {e}. Retry {retries}/{_max_retries}")
                if retries < _max_retries:
                    time.sleep(_retry_delay * retries)  # Exponential backoff
                    # Reset connection pool on error
                    global _connection_pool, _channel_pool
                    if _connection_pool and _connection_pool.is_open:
                        try:
                            _connection_pool.close()
                        except:
                            pass
                    _connection_pool = None
                    _channel_pool = None
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

        logger.error(f"Failed after {_max_retries} retries: {last_exception}")
        raise last_exception

    return wrapper


def get_connection():
    """Get a connection from the pool or create a new one."""
    global _connection_pool

    if _connection_pool is None or not _connection_pool.is_open:
        logger.info("Creating new RabbitMQ connection")
        _connection_pool = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_URL, 
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD),
                heartbeat=60,  # Add heartbeat to detect connection issues
                blocked_connection_timeout=30  # Timeout for blocked connections
            )
        )

    return _connection_pool


def get_channel():
    """Get a channel from the pool or create a new one."""
    global _channel_pool

    if _channel_pool is None or _channel_pool.is_closed:
        connection = get_connection()
        _channel_pool = connection.channel()

    return _channel_pool


@with_connection_retry
def publish_message(message: str, queue_name: str):
    """Publish a message to the queue

    This function will publish a message to the queue using a connection from the pool."""
    try:
        channel = get_channel()
        # Ensure queue exists
        channel.queue_declare(queue=queue_name, durable=True,
                arguments={
                    "x-dead-letter-exchange": "dead_letter_exchange",
                    "x-dead-letter-routing-key": queue_name,
                })
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        logger.debug(f"Published message to {queue_name}: {message}")
    except Exception as e:
        logger.error(f"Error publishing message to {queue_name}: {e}")
        raise


@with_connection_retry
def retry_failed(queue_name: str):
    """Read all the messages from our dead letter queue and republish them to the original queue,
    but only if they match the queue name we are interested in. Ignore all other messages.

    This function will read all the messages from our dead letter queue and republish them to the original queue,
    but only if they match the queue name we are interested in. Ignore all other messages."""
    try:
        channel = get_channel()
        dead_letter_queue = channel.queue_declare(f'dead_letter_queue_{queue_name}')

        messages = dead_letter_queue.method.message_count
        logger.info(f"{messages} messages in the dead letter queue for {queue_name}")

        for i in range(messages):
            method_frame, header_frame, body = channel.basic_get(f'dead_letter_queue_{queue_name}')
            if method_frame:
                logger.info(f"Republishing message from dead letter queue: {body.decode()}")
                channel.basic_publish(exchange='', routing_key=queue_name, body=body)
                channel.basic_ack(method_frame.delivery_tag)
            else:
                logger.info('No more messages in dead letter queue')
                break
    except Exception as e:
        logger.error(f"Error retrying failed messages for {queue_name}: {e}")
        raise


async def wait_for_close(channel):
    """Wait for the channel to be closed

    This function will wait for the channel to be closed and log when it happens."""
    try:
        while not channel.is_closed:
            await asyncio.sleep(1)
        logger.info("Channel closed")
    except Exception as e:
        logger.error(f"Error in wait_for_close: {e}")

import asyncio
import aio_pika
import logging

logger = logging.getLogger(__name__)


async def setup_rabbitmq(queues: list[tuple[str, callable]]):
    """Setup RabbitMQ connection, channel, queues, and consumers with robust error handling"""
    logger.info("Setting up RabbitMQ connection and channel")

    try:
        # Robust connection handles reconnects, re-declarations, and heartbeats automatically
        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
            host=RABBITMQ_URL,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USERNAME,
            password=RABBITMQ_PASSWORD,
            heartbeat=60,
        )

        # Create a channel
        channel: aio_pika.RobustChannel = await connection.channel()

        # Set QoS early for fair dispatch
        await channel.set_qos(prefetch_count=1)

        # Declare the dead letter exchange
        dead_letter_exchange = await channel.declare_exchange(
            "dead_letter_exchange",
            aio_pika.ExchangeType.DIRECT
        )

        # Set up queues and consumers
        for queue_name, callback in queues:
            # Dead-letter queue
            dead_letter_queue = await channel.declare_queue(
                f"dead_letter_queue_{queue_name}",
                durable=True,
            )
            await dead_letter_queue.bind(dead_letter_exchange, routing_key=queue_name)

            # Main queue with DLQ configuration
            queue = await channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "dead_letter_exchange",
                    "x-dead-letter-routing-key": queue_name,
                },
            )

            # Consumer
            await queue.consume(callback)
            logger.info(f"Consumer set up for queue: {queue_name}")

        # Monitor connection closure
        def on_close(fut: asyncio.Future):
            exc = fut.exception()
            if exc:
                logger.warning(f"RabbitMQ connection closed with error: {exc}")
            else:
                logger.info("RabbitMQ connection closed cleanly")

        logger.info("RabbitMQ setup completed successfully")
        return connection, channel

    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise
    except Exception:
        logger.exception("Unexpected error in setup_rabbitmq")
        raise



if __name__ == "__main__":
    """Main function to run the script

    This function will run the script and setup the RabbitMQ connection and channel."""
    try:
        logger.info('Waiting for messages. To exit press CTRL+C')

        # Create event loop
        loop = asyncio.get_event_loop()

        # Example queue setup - replace with actual queues in production
        async def example_callback(message):
            async with message.process():
                logger.info(f"Received message: {message.body.decode()}")

        # Setup RabbitMQ with example queue
        queues = [("example_queue", example_callback)]

        # Run the setup
        channel = loop.run_until_complete(setup_rabbitmq(queues))

        # Keep the loop running
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Interrupted')
        # Close connections gracefully
        if 'channel' in locals() and channel:
            loop.run_until_complete(channel.close())
        if loop.is_running():
            loop.stop()
        loop.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
