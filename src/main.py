"""
This script automates the process of fetching a watchlist from Plex, searching for torrents,
downloading them, and transferring the files to a remote server.

Modules:
- src.plex: Provides the PlexAPI class to interact with Plex.
- src.tl: Contains functions for fetching torrent data, downloading torrents, and transferring files.

Functions:
- is_series(title): Determines if a title is a series based on its format.
- fetch_watchlist(plex_api): Fetches the watchlist from Plex.
- search_torrents(query): Searches for torrents based on a query.
- download_and_transfer_torrent(torrent, media_type): Downloads a torrent and transfers it to a remote server.
- process_show(item): Processes a show by searching and downloading its seasons.
- process_movie(item): Processes a movie by searching and downloading it.
- process_watchlist_item(item): Processes an item from the watchlist (either a show or a movie).
- main(): Main entry point for the script.
"""

import logging
from src.plex import PlexAPI
from src.tl import fetch_torrentleech_data, scp_file_to_remote, download_torrent
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def is_series(title: str) -> bool:
    """
    Determines if the given title is a series.

    Args:
        title (str): The title to check.

    Returns:
        bool: True if the title is a series, False otherwise.
    """
    return "S0" in title


def fetch_watchlist(plex_api):
    """
    Fetches the watchlist from Plex.

    Args:
        plex_api (PlexAPI): An instance of the PlexAPI class.

    Returns:
        list: A list of items in the watchlist.
    """
    logging.info("Fetching watchlist from Plex.")
    watchlist = plex_api.fetch_watchlist()
    if not watchlist:
        logging.warning("No items found in the watchlist.")
    return watchlist or []


def search_torrents(query):
    """
    Searches for torrents based on the given query.

    Args:
        query (str): The search query.

    Returns:
        list: A list of torrents matching the query.
    """
    logging.info("Searching for torrents with query: %s", query)
    result = fetch_torrentleech_data(query)["torrentList"]
    if not result:
        logging.warning("No torrents found for query: %s", query)
    return result


def download_and_transfer_torrent(torrent, media_type):
    """
    Downloads a torrent and transfers it to a remote server.

    Args:
        torrent (dict): The torrent metadata.
        media_type (str): The type of media (e.g., 'series' or 'films').
    """
    local_file = torrent["filename"]
    logging.info("Downloading torrent: %s", local_file)
    download_torrent(torrent["fid"], torrent["filename"], torrent["filename"])

    remote_path = f"/home/blitzcrank/watch/qbittorrent/{media_type}/{local_file}"
    logging.info("Transferring file %s to remote server.", local_file)
    remote_host = os.getenv("REMOTE_HOST")
        remote_port = int(os.getenv("REMOTE_PORT", 22))
        username = os.getenv("REMOTE_USERNAME")
        password = os.getenv("REMOTE_PASSWORD")
        remote_path_base = os.getenv("REMOTE_PATH_BASE")

        scp_file_to_remote(
            file_path=local_file,
            remote_host=remote_host,
            remote_port=remote_port,
            username=username,
            password=password,
            remote_path=f"{remote_path_base}/{local_file}",
        )
    logging.info("File %s successfully transferred.", local_file)


def process_show(item):
    """
    Processes a show by searching for and downloading its seasons.

    Args:
        item (dict): The show metadata.
    """
    logging.info("Processing show: %s", item["title"])
    for season in range(1, 10):
        query = f"{item['title']} S{str(season).zfill(2)}"
        result = search_torrents(query)
        if not result:
            continue
        media_type = "series"
        download_and_transfer_torrent(result[0], media_type)


def process_movie(item):
    """
    Processes a movie by searching for and downloading it.

    Args:
        item (dict): The movie metadata.
    """
    query = f"{item['title']} {item['year']}"
    result = search_torrents(query)
    if not result:
        return
    media_type = "films"
    download_and_transfer_torrent(result[0], media_type)


def process_watchlist_item(item):
    """
    Processes an item from the watchlist (either a show or a movie).

    Args:
        item (dict): The watchlist item metadata.
    """
    if item["type"] == "show":
        process_show(item)
    else:
        process_movie(item)
    logging.info("Successfully processed item: %s", item["title"])


def main():
    """
    Main entry point for the script. Fetches the Plex watchlist and processes each item.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Fetch the Plex token from environment variables
    plex_token = os.getenv("PLEX_TOKEN")
    plex_api = PlexAPI(plex_token)

    watchlist = fetch_watchlist(plex_api)
    for item in watchlist:
        process_watchlist_item(item)

    logging.info("All items processed successfully.")


if __name__ == "__main__":
    main()
