def deduplicate_url_list(lines):
    found = {}
    duplicates = {}
    lines = [l.strip() for l in lines]
    new_file = ""
    for line in lines:
        if not found.get(line) is True:
            found[line] = True
            new_file += f"{line}\n"
        else:
            duplicates[line] = 1 + duplicates.get(line, 0)
    print(f"Removed {len(duplicates.keys())} duplicate urls")
    for key in duplicates.keys():
        print(f"{duplicates[key]} instances of {key}")
    return new_file.split("\n")
