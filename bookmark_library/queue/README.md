# Queue Module

The `queue` module manages the asynchronous processing of bookmarks using RabbitMQ. It handles message queuing, background tasks, and worker processes for different types of operations.

## Components

### `background_job.py`

Sets up and manages background tasks for processing queue messages.

**Key Functions:**
- `initiate_background_tasks()`: Initializes the background tasks for processing queue messages.
- `start_background_thread(loop)`: Starts a background thread with an asyncio event loop.

### `rabbitmq.py`

Handles the integration with RabbitMQ for message queuing.

**Key Functions:**
- `setup_rabbitmq(loop, queues)`: Sets up RabbitMQ connections and channels.
- `publish_message(message, queue_name)`: Publishes a message to a specified queue.
- `retry_failed(queue_name)`: Retries failed messages from a specified queue.

### `queue_names.py`

Defines constants for queue names used in the application.

**Constants:**
- `INGEST_URL_QUEUE_NAME`: Queue for URL ingestion tasks.
- `SUMMARIZE_URL_QUEUE_NAME`: Queue for URL summarization tasks.

## Subdirectories

### `workers/`

Contains worker implementations for different queue types.

#### `ingest_url_queue.py`

Handles the processing of URLs in the ingest queue.

**Key Functions:**
- `get_bookmark_manager_ingest_url_queue()`: Returns the queue configuration for URL ingestion.

#### `summarize_url_queue.py`

Handles the processing of URLs in the summarize queue.

**Key Functions:**
- `get_bookmark_manager_summarize_url_queue()`: Returns the queue configuration for URL summarization.

## Architecture

The queue system uses a producer-consumer pattern:

1. **Producers** (CLI commands, bulk ingest) publish messages to queues
2. **Consumers** (workers) process messages from queues asynchronously
3. **Background tasks** manage the lifecycle of consumers

## Error Handling

The queue system includes error handling mechanisms:
- Failed messages are moved to error queues
- Retry functionality allows reprocessing of failed messages
- Error logging provides visibility into processing issues

## Usage

The queue module is typically used through the CLI interface or the main application:

```python
# Publishing a message to a queue
from bookmark_library.queue.rabbitmq import publish_message
from bookmark_library.queue.queue_names import INGEST_URL_QUEUE_NAME

publish_message("https://example.com", INGEST_URL_QUEUE_NAME)

# Starting background tasks
from bookmark_library.queue.background_job import initiate_background_tasks

initiate_background_tasks()
```