from bookmark_library.library_db.schema.record_convert import url_record_to_db_record


def update_record_query(url, database):
    if url["dirty"]:
        try:
            db_record = url_record_to_db_record(url)
            cursor = database.cursor()
            if db_record[4] is not None or db_record[5] is not None:
                cursor.execute("UPDATE url SET title = %s, text = %s, html = %s, summary = %s WHERE id = %s", [db_record[3], db_record[4], db_record[5], db_record[6], db_record[0]])
            else:
                cursor.execute("UPDATE url SET title = %s, summary = %s WHERE id = %s", [db_record[3], db_record[6], db_record[0]])
            database.commit()
            cursor.close()
            print(f"Updated: {url['url']}")

        except Exception as e:
            print(f"Error updating {url}: {e}")
            database.rollback()
            raise e
