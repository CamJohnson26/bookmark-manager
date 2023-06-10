import psycopg2


def create_record_query(url, database):
    try:
        print('Creating...')
        cursor = database.cursor()
        cursor.execute("INSERT INTO url (id, created_at, url, title, text, html) VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s)", [url, None, None, None])
        # Don't return until the transaction has completed and the database is updated.
        database.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creating {url}: {e}")
        database.rollback()
        raise e
