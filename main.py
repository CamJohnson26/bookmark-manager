from dotenv import load_dotenv

from bookmark_library.queue.background_job import initiate_background_tasks
import asyncio

load_dotenv()

print('Initializing...')

async def main():

    # Keep the event loop running
    # Create an Event to keep the script running
    stop_event = asyncio.Event()

    # Wait indefinitely
    await stop_event.wait()


if __name__ == '__main__':
    print("Consuming messages from the queue")
    initiate_background_tasks()
    asyncio.run(main())

