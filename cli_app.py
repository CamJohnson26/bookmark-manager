from cmd import Cmd

from dotenv import load_dotenv

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
            print(f"{url}")
            return

    def do_exit(self, args):
        """Exit the app."""
        raise SystemExit()


if __name__ == '__main__':
    CLIApp().cmdloop("Enter a command (greet, exit):")
