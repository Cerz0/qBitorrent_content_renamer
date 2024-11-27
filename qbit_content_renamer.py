import re
import requests

# Configuration
qbittorrent_url = "http://localhost:8080"  # Adjust this URL if necessary
username = "admin"  # Your qBittorrent username
password = "admin"  # Your qBittorrent password

# List of renaming patterns and their replacements
renaming_rules = [
    # Example rule: Rename Zhu_Xian to Jade_Dynasty and adjust episode format
    (r"\[Hall_of_C\] Zhu_Xian_(S\d)_(\d+)", r"[Hall_of_C] Jade_Dynasty_\1E\2"),
    # Add more rules here as needed for other series
]

def authenticate():
    """Authenticate with the qBittorrent API."""
    session = requests.Session()
    response = session.post(f"{qbittorrent_url}/api/v2/auth/login", data={"username": username, "password": password})
    if response.status_code != 200 or response.text != "Ok.":
        raise Exception("Failed to authenticate with qBittorrent.")
    return session

def get_torrents(session):
    """Fetch the list of torrents."""
    response = session.get(f"{qbittorrent_url}/api/v2/torrents/info")
    response.raise_for_status()
    return response.json()

def rename_file(session, torrent_hash, old_path, new_path):
    """Rename a file in a torrent."""
    payload = {
        "hash": torrent_hash,
        "oldPath": old_path,
        "newPath": new_path
    }
    response = session.post(f"{qbittorrent_url}/api/v2/torrents/renameFile", data=payload)
    if response.status_code != 200:
        print(f"Failed to rename file: {old_path} -> {new_path} (Error: {response.text})")
    else:
        print(f"Renamed file: {old_path} -> {new_path}")

def apply_renaming_rules(file_name):
    """
    Apply renaming rules using regex.
    Iterate over all defined rules and apply the first match found.
    """
    for pattern, replacement in renaming_rules:
        new_name = re.sub(pattern, replacement, file_name)
        if new_name != file_name:  # If a rule matches and changes the name
            return new_name
    return file_name  # Return the original name if no rules match

def main():
    session = authenticate()
    torrents = get_torrents(session)

    for torrent in torrents:
        torrent_hash = torrent["hash"]
        torrent_name = torrent["name"]
        files_response = session.get(f"{qbittorrent_url}/api/v2/torrents/files", params={"hash": torrent_hash})
        files_response.raise_for_status()
        files = files_response.json()

        for file in files:
            old_path = file["name"]
            new_path = apply_renaming_rules(old_path)
            
            # Rename only if the name changes
            if old_path != new_path:
                rename_file(session, torrent_hash, old_path, new_path)

if __name__ == "__main__":
    main()
