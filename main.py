from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
database = psycopg2.connect(DATABASE_URL)
cursor = database.cursor()
cursor.execute("SELECT * FROM url")
print(cursor.fetchall())

