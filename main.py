import csv
import functools
import glob
import re
import os

import pandas
import requests

from bs4 import BeautifulSoup

FIRST_YEAR = 2000
LAST_YEAR = 2022
FEDERAL_YEARS = r"https://www.aec.gov.au/Elections/federal_elections"

MAXIMUM_FILE_SIZE = 2e8
HTML_HEADER_CONTENT_TYPE_KEY = 'content-type'
HTML_HEADER_CONTENT_LENGTH_KEY = 'content-length'
HTML_HEADER_CONTENT_DISPOSITION_KEY = 'content-disposition'
DIRECTORY_DIVIDER_PATTERN = re.compile(r'[^a-zA-Z]+')
FILENAME_PATTERN = re.compile(r'filename=(.+)')


class Inventory(list):
    """
    List of items. __iter__() method returns elements in alphabetical
    order
    """

    def __init__(self):
        list.__init__(self)
        self._sorted = False

    def __iter__(self):
        if not self._sorted:
            self.sort()
            self._sorted = True
        return list.__iter__(self)

    def __call__(self, new_item):
        if new_item not in self:
            self.append(new_item)

    def download_from_url(self, url, target_type="application/octet-stream"):
        header = requests.head(url, allow_redirects=True).headers
        content_type = str(header.get(HTML_HEADER_CONTENT_TYPE_KEY)).lower()
        if content_type == target_type:
            self._download_target(header, url)
        else:
            self._add_item(f"Didn't download {url}. "
                          f"Wrong content type: {content_type}")

    def _download_target(self, header, url):
        content_length = float(header.get(HTML_HEADER_CONTENT_LENGTH_KEY, None))
        if content_length and content_length <= MAXIMUM_FILE_SIZE:
            self._download_file(url)
        else:
            self._add_item(f"Didn't download f{url}. "
                           f"Size of file exceeds {MAXIMUM_FILE_SIZE}")

    def _download_file(self, url):
        get_request = requests.get(url, allow_redirects=True)
        filename = Inventory.guess_filename(get_request, url)
        if filename:
            subdirectories = [section.lower() for section in
                              DIRECTORY_DIVIDER_PATTERN.split(filename)
                              if len(section) > 1]
            target_path = os.path.join(*subdirectories)
            os.makedirs(target_path, exist_ok=True)
            with open(os.path.join(target_path, filename), "wb") as target_file:
                target_file.write(get_request.content)
        else:
            self._add_item(f"Didn't download f{url}. Can't guess the filename.")

    def _add_item(self, new_item):
        if new_item not in self:
            self(new_item)
            print(new_item)

    @staticmethod
    def guess_filename(get_request, url):
        if HTML_HEADER_CONTENT_DISPOSITION_KEY in get_request.headers:
            return FILENAME_PATTERN.findall(
                get_request.headers[HTML_HEADER_CONTENT_DISPOSITION_KEY])[0]
        return url.split("/")[-1]


if __name__ == "__main__":
    inv = Inventory()
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        year_url = f"{FEDERAL_YEARS}/{year}"
        soup = BeautifulSoup(requests.get(f"{year_url}/downloads.htm").text,
                             'html.parser')
        for node in soup.find_all('a'):
            href_get = node.get('href')
            if href_get:
                if href_get.endswith('.csv'):
                    inv.download_from_url(f"{year_url}/{node.get('href')}")
