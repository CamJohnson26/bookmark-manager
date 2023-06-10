def create_record_query(url, database):
    cursor = database.cursor()
    cursor.execute("INSERT INTO url (id, created_at, url, title, text, html) VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s)", [url, None, None, None])
    database.commit()
    print(f"Created: {url}")
