import sys

import asyncio
import aio_pika
import pika
from dotenv import load_dotenv
import os

load_dotenv()
token = os.environ.get("api-token")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")


def publish_message(message: str, queue_name: str):
    """Publish a message to the queue

    This function will publish a message to the queue."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL, port=RABBITMQ_PORT,
                                                                   credentials=pika.PlainCredentials(RABBITMQ_USERNAME,
                                                                                                     RABBITMQ_PASSWORD)))
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    connection.close()


def retry_failed(queue_name: str):
    """Read all the messages from our dead letter queue and republish them to the original queue,
    but only if they match the queue name we are interested in. Ignore all other messages.

    This function will read all the messages from our dead letter queue and republish them to the original queue,
    but only if they match the queue name we are interested in. Ignore all other messages."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL, port=RABBITMQ_PORT,
                                                                   credentials=pika.PlainCredentials(RABBITMQ_USERNAME,
                                                                                                     RABBITMQ_PASSWORD)))
    channel = connection.channel()
    dead_letter_queue = channel.queue_declare(f'dead_letter_queue_{queue_name}')

    messages = dead_letter_queue.method.message_count
    print(f" [*] {messages} messages in the dead letter queue")

    for i in range(messages):
        method_frame, header_frame, body = channel.basic_get(f'dead_letter_queue_{queue_name}')
        if method_frame:
            print(f" [x] Republishing {body.decode()}")
            channel.basic_publish(exchange='', routing_key=queue_name, body=body)
            channel.basic_ack(method_frame.delivery_tag)
        else:
            print(' [x] No message returned')
            break
    connection.close()


async def wait_for_close(channel):
    """Wait for the channel to be closed

    This function will wait for the channel to be closed."""
    while not channel.is_closed:
        await asyncio.sleep(1)


async def setup_rabbitmq(loop: asyncio.AbstractEventLoop, queues: list[tuple[str, callable]]):
    """Setup RabbitMQ connection and channel"""
    print(' [*] Setting up RabbitMQ connection and channel')
    connection = await aio_pika.connect_robust(host=RABBITMQ_URL, port=RABBITMQ_PORT,
                                               login=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD, loop=loop)

    channel = await connection.channel()

    # Declare the dead letter exchange
    dead_letter_exchange = await channel.declare_exchange('dead_letter_exchange', aio_pika.ExchangeType.DIRECT)

    for queue_name, callback in queues:
        # Declare the dead letter queue and bind it to the dead letter exchange
        dead_letter_queue = await channel.declare_queue(f'dead_letter_queue_{queue_name}')
        await dead_letter_queue.bind(dead_letter_exchange, routing_key=queue_name)
        queue = await channel.declare_queue(queue_name, arguments={
            'x-dead-letter-exchange': 'dead_letter_exchange',
            'x-dead-letter-routing-key': queue_name
        })
        await queue.consume(callback)

    # Wait for the channel to be closed
    loop.create_task(wait_for_close(channel))

    return channel


if __name__ == "__main__":
    """Main function to run the script

    This function will run the script and setup the RabbitMQ connection and channel."""
    try:
        print(' [*] Waiting for messages. To exit press CTRL+C')
        setup_rabbitmq()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
