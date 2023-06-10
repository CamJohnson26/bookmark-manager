from cmd import Cmd

from dotenv import load_dotenv


from bookmark_library.bulk_ingest import bulk_ingest
from bookmark_library.queue.background_job import initiate_background_tasks
from bookmark_library.queue.queue_names import INGEST_URL_QUEUE_NAME, SUMMARIZE_URL_QUEUE_NAME
from bookmark_library.queue.rabbitmq import publish_message, retry_failed

load_dotenv()


# token = os.environ.get("")


class CLIApp(Cmd):
    """A simple CLI app."""
    prompt = '>>> '

    def do_ingest(self, args):
        """Greet a person."""
        urls = args.rsplit(" ", 1)
        if len(urls) >= 1:
            url = urls[0]
            publish_message(url, INGEST_URL_QUEUE_NAME)
            print(f"{url}")
            return

    def do_bulk_ingest(self, args):
        """Ingest a list of urls from the input/ingest.txt file."""
        bulk_ingest()

    def do_retry_ingest(self, args):
        retry_failed(INGEST_URL_QUEUE_NAME)

    def do_retry_summarize(self, args):
        retry_failed(SUMMARIZE_URL_QUEUE_NAME)
    def do_consume(self, args):
        """Consume messages from the queue."""
        print("Consuming messages from the queue")
        initiate_background_tasks()

    def do_exit(self, args):
        """Exit the app."""
        raise SystemExit()


if __name__ == '__main__':
    CLIApp().cmdloop("Enter a command (greet, exit):")
