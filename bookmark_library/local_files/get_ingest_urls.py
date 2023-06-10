def get_ingest_urls():
    filename = "input/ingest.txt"
    with open(filename) as f:
        lines = f.readlines()
    return [l.strip() for l in lines]
