from bookmark_library.library_db.schema.record_convert import url_record_to_db_record


def update_record_query(url, connection_pool):
    if url["dirty"]:
        conn = None
        try:
            db_record = url_record_to_db_record(url)
            conn = connection_pool.getconn()
            cursor = conn.cursor()
            if db_record[4] is not None or db_record[5] is not None:
                cursor.execute("UPDATE url SET title = %s, text = %s, html = %s, summary = %s WHERE id = %s", [db_record[3], db_record[4], db_record[5], db_record[6], db_record[0]])
            else:
                cursor.execute("UPDATE url SET title = %s, summary = %s WHERE id = %s", [db_record[3], db_record[6], db_record[0]])
            conn.commit()
            cursor.close()
            print(f"Updated: {url['url']}")

        except Exception as e:
            print(f"Error updating {url}: {e}")
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                connection_pool.putconn(conn)
