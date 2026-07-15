import os


def get_firefox_binary():
    configured_path = os.getenv("FIREFOX_BINARY")
    if configured_path:
        return configured_path

    snap_binary = "/snap/firefox/current/usr/lib/firefox/firefox"
    if os.path.isfile(snap_binary) and os.access(snap_binary, os.X_OK):
        return snap_binary

    return "/usr/bin/firefox"
