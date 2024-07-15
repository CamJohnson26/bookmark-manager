from dotenv import load_dotenv

from bookmark_library.queue.background_job import initiate_background_tasks

load_dotenv()

if __name__ == '__main__':
    print("Consuming messages from the queue")
    initiate_background_tasks()