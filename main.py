import re
import os
import requests
import wordsegment

from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema, InvalidSchema

ELECTIONS_PAGE = r"https://results.aec.gov.au/"
MAXIMUM_FILE_SIZE = 2e8

HTML_HEADER_CONTENT_TYPE_KEY = 'content-type'
HTML_HEADER_CONTENT_LENGTH_KEY = 'content-length'
HTML_HEADER_CONTENT_DISPOSITION_KEY = 'content-disposition'
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
        if new_item in self:
            return False
        self.append(new_item)
        return True

    def download_from_url(self, url, check_type=False,
                          target_type="application/octet-stream"):
        header = requests.head(url, allow_redirects=True).headers
        if check_type:
            content_type = str(header.get(HTML_HEADER_CONTENT_TYPE_KEY)).lower()
            if content_type == target_type:
                self._download_target(header, url)
            else:
                print(f"Didn't download {url}. Wrong type: {content_type}")
        else:
            self._download_target(header, url)

    def _download_target(self, header, url):
        content_length = float(header.get(HTML_HEADER_CONTENT_LENGTH_KEY, None))
        if content_length and content_length <= MAXIMUM_FILE_SIZE:
            self._download_file(url)
        else:
            print(f"Didn't download {url}. Size exceeds {MAXIMUM_FILE_SIZE}")

    def _download_file(self, url):
        get_request = requests.get(url, allow_redirects=True)
        filename = Inventory.guess_filename(get_request, url)
        if filename:
            target_path = os.path.join(*wordsegment.segment(filename.lower()))
            os.makedirs(target_path, exist_ok=True)
            with open(os.path.join(target_path, filename), "wb") as target_file:
                target_file.write(get_request.content)
        else:
            print(f"Didn't download {url}. Can't guess the filename.")

    @staticmethod
    def guess_filename(get_request, url):
        if HTML_HEADER_CONTENT_DISPOSITION_KEY in get_request.headers:
            return FILENAME_PATTERN.findall(
                get_request.headers[HTML_HEADER_CONTENT_DISPOSITION_KEY])[0]
        return url.split("/")[-1]

    def follow(self, url, verbose=True, level=0, target_extension='.csv',
               follow_text='download'):
        if url and self(url):
            url_split_on_slashes = url.split("/")
            try:
                stem = "/".join(url_split_on_slashes[:-1])
                [self.next_node(
                    follow_text, level, node, stem, target_extension) for node
                    in BeautifulSoup(requests.get(url).text, 'html.parser'
                                     ).find_all('a') if node]
                if verbose:
                    print(' '.join([". " * level, url_split_on_slashes[-1]]))
            except InvalidSchema as schemaException:
                if verbose:
                    print(f"Didn't download {url}. {str(schemaException)}")
            except MissingSchema:
                pass

    def next_node(self, follow_text, level, node, stem, target_extension,
                  verbose):
        node_get = node.get('href')
        if node_get:
            next_url = f"{stem}/{node_get}"
            if node.string and follow_text in node.string.lower():
                self.follow(next_url, level=level+1, verbose=verbose)
            if node_get.endswith(target_extension):
                inv.download_from_url(next_url)


if __name__ == "__main__":
    wordsegment.load()
    inv = Inventory()
    [inv.follow(req_node.get('href')) for req_node in BeautifulSoup(
        requests.get(ELECTIONS_PAGE).text, 'html.parser').find_all('a')]
