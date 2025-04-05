"""
This script provides functionality to interact with TorrentLeech, including:
- Fetching torrent data based on a search query.
- Downloading torrent files.
- Transferring files to a remote host using SCP.

It is designed to automate the process of searching, downloading, and uploading torrents.
"""

import requests
import paramiko
from scp import SCPClient
from dotenv import load_dotenv
import os


def fetch_torrentleech_data(search_query):
    """
    Fetch torrent data from TorrentLeech based on a search query.

    :param search_query: The search term to query torrents.
    :return: JSON response containing torrent data.
    """
    url = f"https://www.torrentleech.org/torrents/browse/list/facets/name%3A720p/query/{search_query}/categories/14/orderby/completed/order/desc"
    headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }
    cookies = {
        "cf_clearance": "0t4YzERcG2dOXcNlX4t5uwLoaEY_PxQCwjHF0XWC6cM-1738978751-1.2.1.1-7lRK3pLa8p4SSQn3qgYce2a8ij6xhILJWoLC8f5xvvp4yPXUYQtEVzyOe__ySx8M4iH2hyN3unZpifrQOKi7vdxL3yBtlJpq3CaypMbeIdbtigwTcF.PG8XzKW7.dCDAQFTbeBjC.dMH.g5xR9FeIlpOvSfk.aShcirPJzej7CPQWzS1BSODPyO0rBD_XhGi2KxMbeH3ZfMYW8Km2dFL66Whl4ZA5qUgGUM_r.2A2DC5j8_VbrkJRN9nyvAkdi5LSQC3IwbECaGVIhgjGuBa3f.l7xkU7dEa8ft.3kM9cObgrRcJZ4wrz2d04jmLly91souTKdRAK7x6K3eiWGD8yg",
        "tluid": "1850863",
        "tlpass": "44c90bf8a914c94cd153d31f324fab48e711be51",
        "PHPSESSID": "qqc8aohdh8aguna596432du16r",
    }
    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    response.raise_for_status()
    return response.json()


def download_torrent(fid, filename, save_to):
    """
    Download a torrent file from TorrentLeech.

    :param fid: The file ID of the torrent.
    :param filename: The filename of the torrent.
    :param save_to: The path to save the downloaded file.
    """
    url = f"https://www.torrentleech.org/download/{fid}/{filename}"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }
    cookies = {
        "cf_clearance": "0t4YzERcG2dOXcNlX4t5uwLoaEY_PxQCwjHF0XWC6cM-1738978751-1.2.1.1-7lRK3pLa8p4SSQn3qgYce2a8ij6xhILJWoLC8f5xvvp4yPXUYQtEVzyOe__ySx8M4iH2hyN3unZpifrQOKi7vdxL3yBtlJpq3CaypMbeIdbtigwTcF.PG8XzKW7.dCDAQFTbeBjC.dMH.g5xR9FeIlpOvSfk.aShcirPJzej7CPQWzS1BSODPyO0rBD_XhGi2KxMbeH3ZfMYW8Km2dFL66Whl4ZA5qUgGUM_r.2A2DC5j8_VbrkJRN9nyvAkdi5LSQC3IwbECaGVIhgjGuBa3f.l7xkU7dEa8ft.3kM9cObgrRcJZ4wrz2d04jmLly91souTKdRAK7x6K3eiWGD8yg",
        "tluid": "1850863",
        "tlpass": "44c90bf8a914c94cd153d31f324fab48e711be51",
        "PHPSESSID": "qqc8aohdh8aguna596432du16r",
    }
    response = requests.get(
        url, headers=headers, cookies=cookies, stream=True, timeout=10
    )
    response.raise_for_status()

    with open(save_to, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"File downloaded successfully: {save_to}")


def scp_file_to_remote(
    file_path, remote_host, remote_port, username, password, remote_path
):
    """
    Transfer a file to a remote host using SCP.

    :param file_path: Path to the local file to be uploaded.
    :param remote_host: Remote host address.
    :param remote_port: Remote host port (default is 22).
    :param username: Username for authentication.
    :param password: Password for authentication.
    :param remote_path: Path on the remote host where the file will be uploaded.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        remote_host, port=remote_port, username=username, password=password
    )

    transport = ssh_client.get_transport()
    if transport is None:
        raise ValueError("Failed to get transport from SSH client.")
    with SCPClient(transport) as scp_client:
        scp_client.put(file_path, remote_path)
    print(f"File '{file_path}' successfully uploaded to '{remote_path}'")


