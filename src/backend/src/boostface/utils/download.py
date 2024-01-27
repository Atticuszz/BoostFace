"""
model_file_url:https://drive.google.com/file/d/1MgFEo4SAaLgAzmuEyu4KHKaGfiKoOeQ7/view?usp=sharing
"""

import sys
import zipfile
from pathlib import Path
from time import time

import google.auth.transport.requests
import requests
from google.oauth2.service_account import Credentials


def download_and_unzip_file():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    credentials = Credentials.from_service_account_file('google_driver_api_key.json', scopes=SCOPES)

    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    authed_session = google.auth.transport.requests.AuthorizedSession(credentials)

    file_id = '1MgFEo4SAaLgAzmuEyu4KHKaGfiKoOeQ7'
    file_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    save_path = Path().cwd().parent / "model_zoo" / "models.zip"

    # Check total file size only once
    response = authed_session.head(file_url)
    total_size = int(response.headers.get('content-length', 0))
    print(f"Total size: {total_size / 1024 / 1024:.2f} MB")

    timeout_duration = 60  # 60 seconds timeout duration

    while True:
        if save_path.exists():
            resume_byte_pos = save_path.stat().st_size
        else:
            resume_byte_pos = 0

        custom_headers = {'Range': f"bytes={resume_byte_pos}-"}
        response = authed_session.get(file_url, headers=custom_headers, stream=True)

        start_time = time()
        downloaded_size = resume_byte_pos
        last_print_time = start_time
        last_print_size = downloaded_size

        write_mode = 'wb' if resume_byte_pos == 0 else 'ab'

        with open(save_path, write_mode) as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    downloaded_size += len(chunk)

                    elapsed_since_last_print = time() - last_print_time
                    if elapsed_since_last_print >= timeout_duration:
                        print("\nTimeout reached. Restarting download.")
                        break

                    if downloaded_size - last_print_size >= 10 * 1024 * 1024:
                        elapsed_time = time() - last_print_time
                        speed = (downloaded_size - last_print_size) / elapsed_time / 1024 / 1024  # MB/s

                        progress = downloaded_size / total_size * 100
                        progress_bar = "=" * int(progress // 2) + " " * (50 - int(progress // 2))

                        sys.stdout.write(
                            f"\rProgress: [{progress_bar}] {progress:.2f}% | {downloaded_size / 1024 / 1024:.2f} MB, speed: {speed:.2f} MB/s")
                        sys.stdout.flush()

                        last_print_time = time()
                        last_print_size = downloaded_size

                    f.write(chunk)
            else:
                break  # exit while loop if download completed

    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(save_path.parent)

    save_path.unlink()

    print("\nFile downloaded, unzipped, and original zip file deleted.")


class GoogleDriveDownloader:
    def __init__(self, file_id, timeout_duration=5):
        self.authed_session = None
        self.file_id = file_id
        self.save_path = Path().cwd().parent / "model_zoo" / "models.zip"
        self.timeout_duration = timeout_duration
        self.total_size = None
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.credentials = Credentials.from_service_account_file('google_driver_api_key.json', scopes=self.SCOPES)

    def authenticate(self):
        request = google.auth.transport.requests.Request()
        self.credentials.refresh(request)
        self.authed_session = google.auth.transport.requests.AuthorizedSession(self.credentials)

    def get_total_size(self):
        file_url = f"https://www.googleapis.com/drive/v3/files/{self.file_id}?alt=media"
        response = self.authed_session.head(file_url)
        self.total_size = int(response.headers.get('content-length', 0))

    def download(self):
        self.authenticate()
        self.get_total_size()

        print(f"\nTotal size: {self.total_size / 1024 / 1024:.2f} MB")

        while True:
            try:
                self._partial_download()
            except (requests.ConnectionError, requests.Timeout, TimeoutError):
                print("\nNetwork error. Retrying...")
                continue
            break

    def _partial_download(self):
        custom_headers = {'Range': f"bytes={self.save_path.stat().st_size}-"} if self.save_path.exists() else {}
        file_url = f"https://www.googleapis.com/drive/v3/files/{self.file_id}?alt=media"
        response = self.authed_session.get(file_url, headers=custom_headers, stream=True)

        start_time = time()
        downloaded_size = self.save_path.stat().st_size if self.save_path.exists() else 0
        last_print_time = start_time
        last_print_size = downloaded_size

        write_mode = 'wb' if not self.save_path.exists() else 'ab'

        with open(self.save_path, write_mode) as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    downloaded_size += len(chunk)

                    elapsed_since_last_print = time() - last_print_time
                    if elapsed_since_last_print >= self.timeout_duration:
                        print("\nTimeout reached. Restarting download.")
                        raise TimeoutError

                    if downloaded_size - last_print_size >= 10 * 1024 * 1024:
                        elapsed_time = time() - last_print_time
                        speed = (downloaded_size - last_print_size) / elapsed_time / 1024 / 1024  # MB/s

                        progress = downloaded_size / self.total_size * 100
                        progress_bar = "=" * int(progress // 2) + " " * (50 - int(progress // 2))

                        sys.stdout.write(
                            f"\rProgress: [{progress_bar}] {progress:.2f}% | {downloaded_size / 1024 / 1024:.2f} MB, speed: {speed:.2f} MB/s")
                        sys.stdout.flush()

                        last_print_time = time()
                        last_print_size = downloaded_size

                    f.write(chunk)

        self._unzip_and_cleanup()

    def _unzip_and_cleanup(self):
        with zipfile.ZipFile(self.save_path, 'r') as zip_ref:
            zip_ref.extractall(self.save_path.parent)

        self.save_path.unlink()

        print("\nFile downloaded, unzipped, and original zip file deleted.")


if __name__ == "__main__":
    downloader = GoogleDriveDownloader(
        file_id='1MgFEo4SAaLgAzmuEyu4KHKaGfiKoOeQ7',
    )
    downloader.download()
