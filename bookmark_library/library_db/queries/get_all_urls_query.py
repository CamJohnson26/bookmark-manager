from bookmark_library.library_db.schema.record_convert import db_record_to_url_record


def get_all_urls_query(database):
    cursor = database.cursor()
    cursor.execute("SELECT id, created_at, url, title, summary FROM url")
    records = cursor.fetchall()
    cursor.close()
    print(f"Fetched {len(records)} records")
    return [db_record_to_url_record(r) for r in records]