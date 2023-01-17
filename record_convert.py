
def db_record_to_url_record(db_record):
    return {
        "id": db_record[0],
        "created_at": db_record[1],
        "url": db_record[2],
        "title": db_record[3],
        "summary": db_record[4],
        # "text": db_record[4],
        # "html": db_record[5],
        "dirty": False
    }


def url_record_to_db_record(db_record):
    return [
        db_record["id"],
        db_record["created_at"],
        db_record["url"],
        db_record["title"],
        db_record.get("text", None),
        db_record.get("html", None),
        db_record["summary"],
    ]
