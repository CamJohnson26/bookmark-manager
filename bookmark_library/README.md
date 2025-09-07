# Bookmark Library Module

The `bookmark_library` module is the core package of the Bookmark Manager application. It contains all the functionality for processing, storing, and retrieving bookmarks.

## Submodules

### `bulk_ingest.py`

Handles the bulk ingestion of URLs from a text file.

**Key Functions:**
- `bulk_ingest()`: Reads URLs from the input/ingest.txt file and publishes them to the ingest queue.

### `get_new_urls.py`

Processes new URLs and extracts basic information.

**Key Functions:**
- Functions for extracting and processing new URLs.

### `get_url_base_fields.py`

Extracts base fields from URLs such as title, domain, etc.

**Key Functions:**
- Functions for extracting base metadata from URLs.

### `get_url_summary_fields.py`

Generates summaries and additional metadata for URLs.

**Key Functions:**
- Functions for generating summaries of web page content.

## Subdirectories

### `library_db/`

Handles database operations for storing and retrieving bookmark data.

### `local_files/`

Manages local file storage for cached content and other data.

### `page_crawler/`

Contains functionality for crawling web pages and extracting content.

**Key Components:**
- `fetch_pdf_url.py`: Fetches and processes PDF documents from URLs.

### `page_parser/`

Parses HTML and other content types to extract relevant information.

### `queue/`

Manages the message queuing system for asynchronous processing.

**Key Components:**
- `background_job.py`: Sets up background tasks for processing queue messages.
- `rabbitmq.py`: Handles RabbitMQ integration.
- `workers/`: Contains worker implementations for different queue types.