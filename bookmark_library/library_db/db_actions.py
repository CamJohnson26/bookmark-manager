from dotenv import load_dotenv

import os

from bookmark_library.library_db.queries.create_record_query import create_record_query

from bookmark_library.library_db.queries.get_all_urls_query import get_all_urls_query
from bookmark_library.library_db.queries.get_url_query import get_url_query
from bookmark_library.library_db.queries.update_record_query import update_record_query

from psycopg2 import pool

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

connection_pool = pool.SimpleConnectionPool(
    1,      # Minimum number of connections
    10,     # Maximum number of connections
    DATABASE_URL
)

def create_record(url):
    return create_record_query(url, connection_pool)


def update_record(url):
    return update_record_query(url, connection_pool)


def get_url(url):
    return get_url_query(url, connection_pool)

def get_all_urls():
    return get_all_urls_query(connection_pool)