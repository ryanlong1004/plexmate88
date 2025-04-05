"""
This module provides functionality to interact with the Plex API,
fetch a user's watchlist, display it in a readable format, and save it to a file.
"""

import json
from typing import Dict, List, Optional

import requests


class PlexAPI:
    """
    A class to interact with the Plex API.
    """

    BASE_URL = "https://discover.provider.plex.tv/library/sections/watchlist/released"

    def __init__(self, plex_token: str):
        """
        Initialize the PlexAPI instance.

        Args:
            plex_token (str): Your Plex authentication token.
        """
        self.plex_token = plex_token
        self.headers = {"Accept": "application/json"}

    def fetch_watchlist(self) -> Optional[List[Dict]]:
        """
        Fetches the Plex watchlist for the user.

        Returns:
            Optional[List[Dict]]: A list of media items in the watchlist, or None if an error occurs.
        """
        url = f"{self.BASE_URL}?X-Plex-Token={self.plex_token}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return self._parse_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching watchlist: {e}")
            return None

    def _parse_response(self, response: requests.Response) -> Optional[List[Dict]]:
        """
        Parse the API response.

        Args:
            response (requests.Response): The HTTP response object.

        Returns:
            Optional[List[Dict]]: Parsed watchlist data or None if parsing fails.
        """
        if not response.content.strip():
            print("Error: Received an empty response from the server.")
            return None
        try:
            data = response.json()
            return data.get("MediaContainer", {}).get("Metadata", [])
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return None


def display_watchlist(watchlist: List[Dict]) -> None:
    """
    Display the watchlist in a readable format.

    Args:
        watchlist (List[Dict]): A list of media items in the watchlist.
    """
    for item in watchlist:
        print(f"Title: {item.get('title', 'Unknown')}")
        print(f"Type: {item.get('type', 'Unknown')}")
        print(f"Year: {item.get('year', 'N/A')}")
        print("-" * 20)


def save_watchlist_to_file(watchlist: List[Dict], filename: str) -> None:
    """
    Save the watchlist to a JSON file.

    Args:
        watchlist (List[Dict]): A list of media items in the watchlist.
        filename (str): The file name to save the watchlist to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(watchlist, file, indent=4)
        print(f"Watchlist saved to {filename}")
    except IOError as e:
        print(f"Error saving watchlist to file: {e}")
