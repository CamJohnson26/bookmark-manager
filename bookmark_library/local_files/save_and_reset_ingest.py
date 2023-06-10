from bookmark_library.local_files.deduplicate_url_list import deduplicate_url_list
from bookmark_library.local_files.get_history_urls import get_history_urls
from bookmark_library.local_files.get_ingest_urls import get_ingest_urls
from bookmark_library.local_files.write_urls_to_file import write_urls_to_file


def save_and_reset_ingest():
    """This function is used to save the ingest.txt contents to history.txt and reset it to an empty file."""
    ingest_urls = get_ingest_urls()
    history_urls = get_history_urls()
    all_urls = ingest_urls + history_urls
    deduplicated_urls = deduplicate_url_list(all_urls)
    write_urls_to_file(deduplicated_urls, "input/history.txt")
    write_urls_to_file([], "input/ingest.txt")
    print(f"Saved {len(deduplicated_urls)} urls to history.txt and reset ingest.txt to an empty file")
