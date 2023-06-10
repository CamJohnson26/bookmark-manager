def write_urls_to_file(urls, filename):
    """This function is used to write a list of urls to a file."""
    with open(filename, 'w') as f:
        for url in urls:
            f.write(f"{url}\n")
    print(f"Wrote {len(urls)} urls to {filename}")