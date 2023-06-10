import psycopg2
from dotenv import load_dotenv

import os

from bookmark_library.library_db.create_record_query import create_record_query

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

database = psycopg2.connect(DATABASE_URL)


def create_record(url):
    create_record_query(url, database)
