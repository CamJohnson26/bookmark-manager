import psycopg2


def create_record_query(url, connection_pool):
    try:
        print('Creating...')
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO url (id, created_at, url, title, text, html) VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s)", [url, None, None, None])
        # Don't return until the transaction has completed and the database is updated.
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creating {url}: {e}")
        conn.rollback()
        raise e
    finally:
        connection_pool.putconn(conn)