import psycopg2
from dotenv import load_dotenv

import os

from bookmark_library.library_db.queries.create_record_query import create_record_query
from bookmark_library.library_db.queries.get_url import get_url_query
from bookmark_library.library_db.queries.update_record_query import update_record_query

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

database = psycopg2.connect(DATABASE_URL)


def create_record(url):
    return create_record_query(url, database)


def update_record(url):
    return update_record_query(url, database)


def get_url(url):
    return get_url_query(url, database)
