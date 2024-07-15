from dotenv import load_dotenv

from bookmark_library.queue.background_job import initiate_background_tasks
import asyncio
import sys

load_dotenv()

print('Initializing...')

async def main():

    # Keep the event loop running
    while True:
        sys.stdout.flush()  # Explicitly flush output
        await asyncio.sleep(3600)  # Sleep for an hour


if __name__ == '__main__':
    print("Consuming messages from the queue")
    initiate_background_tasks()
    asyncio.run(main())

