from bookmark_library.library_db.schema.record_convert import db_record_to_url_record


def get_url_query(url, database):
    cursor = database.cursor()
    cursor.execute("SELECT id, created_at, url, title, summary FROM url WHERE url = %s", [str(url)])
    records = cursor.fetchall()
    cursor.close()
    record = records[0] if len(records) > 0 else None
    if record is not None:
        print(f"Fetched {len(record)} records")
        return db_record_to_url_record(record)
    else:
        print(f"Couldn't find {url}")
        return None
