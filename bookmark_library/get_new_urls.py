from bookmark_library.library_db.db_actions import get_all_urls
from bookmark_library.local_files.deduplicate_url_list import deduplicate_url_list
from bookmark_library.local_files.get_history_urls import get_history_urls
from bookmark_library.local_files.get_ingest_urls import get_ingest_urls


def get_new_urls():
    history = get_history_urls()
    ingest_urls = get_ingest_urls()
    deduplicated_urls = deduplicate_url_list(history + ingest_urls)

    existing_urls = [url["url"] for url in get_all_urls()]
    new_urls = [url for url in deduplicated_urls if url not in existing_urls and url not in history and url != ""]

    return new_urls
