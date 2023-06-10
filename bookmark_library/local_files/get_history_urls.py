def get_history_urls():
    filename = "input/history.txt"
    with open(filename) as f:
        lines = f.readlines()
    return [l.strip() for l in lines]
