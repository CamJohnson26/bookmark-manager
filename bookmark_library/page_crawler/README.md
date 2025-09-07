# Page Crawler Module

The `page_crawler` module is responsible for fetching and processing web content from URLs. It handles different types of web content, including HTML pages and PDF documents.

## Components

### `fetch_pdf_url.py`

This component is responsible for fetching and processing PDF documents from URLs.

**Key Functions:**

- `fetch_pdf_url(url)`: Fetches a PDF from a given URL, downloads it temporarily, extracts the text content, and returns it as HTML.

**Process:**
1. Makes an HTTP request to the URL with appropriate headers
2. Saves the PDF content to a temporary file
3. Uses pdfminer to extract text from the PDF
4. Converts the extracted text to HTML format
5. Removes the temporary file
6. Returns the HTML content

**Error Handling:**
- Handles PDF syntax errors and encryption errors
- Provides error messages when PDFs cannot be read

**Dependencies:**
- requests: For making HTTP requests
- pdfminer: For PDF text extraction
- io.StringIO: For string buffer operations
- os: For file operations

## Usage

The page crawler components are typically used by the queue workers to process URLs asynchronously. They are not usually called directly by user code.

Example usage within the application:

```python
from bookmark_library.page_crawler.fetch_pdf_url import fetch_pdf_url

# Fetch and process a PDF
html_content = fetch_pdf_url("https://example.com/document.pdf")
```