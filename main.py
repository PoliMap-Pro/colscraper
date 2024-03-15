import os
import requests
import wordsegment

from constants import TYPE_KEY, LENGTH_KEY, CONT_DISP, F_PAT, FOLDERS_PATTERN, \
    GET_EXCEPT, DO_NOT_GO_TO_PLACES_ENDING_IN, DO_NOT_GO_TO_PLACES_CONTAINING
from bs4 import BeautifulSoup, ParserRejectedMarkup
from requests.exceptions import InvalidSchema

TOP = (r"https://results.aec.gov.au/", )
TARGET_EXTENSIONS = ('.csv', '.xls', '.xlsx', '.ashx', '.zip', )


class Tally(dict):
    def __setitem__(self, key, value):
        if key in self:
            dict.__setitem__(self, key, self[key] + value)
        else:
            dict.__setitem__(self, key, value)


class Inventory(list):
    def __init__(self, target='download', between=2, depth=15, size=2e8):
        list.__init__(self)
        self.target_links = target
        self.max_between, self.max_depth, self.max_size = between, depth, size

    def __call__(self, new_item):
        if new_item in self:
            return False
        self.append(new_item)
        return True

    def follow(self, url, folders, verb=True, lev=0, ext=TARGET_EXTENSIONS):
        if url:
            url = url.replace(r"///", r"/")
            if self(url):
                if lev < self.max_depth:
                    try:
                        self.tick(ext, folders, lev, url, verb)
                    except (InvalidSchema, ParserRejectedMarkup) as exception:
                        if verb:
                            print(f"Didn't download {url}. {str(exception)}")
                    except GET_EXCEPT:
                        pass

    def tick(self, ext, folders, lev, url, verb):
        usplit = self._get_next_nodes(ext, folders, lev, url, verb)
        if verb:
            print(' '.join([". " * lev, usplit[-1] if usplit[-1] else url]))

    def _get_next_nodes(self, ext, fold, lev, url, verb, parse='html.parser'):
        result = url.split("/")
        stem = "/".join(result[:-1])
        try:
            [self._next_node(lev, node, stem, ext, verb, fold) for node in
             BeautifulSoup(requests.get(url).text, parse).find_all('a') if node]
        except GET_EXCEPT:
            pass
        return result

    def get_year(self, node, getrib='href', year_group=1, char_group=2):
        match = FOLDERS_PATTERN.match(node.string.lower())
        if match:
            self.follow(node.get(getrib), (match.group(year_group), "".join([
                char for char in match.group(char_group) if char.isalpha()])))

    def fetch(self, url, fold, check=False, target="application/octet-stream"):
        if self(url):
            try:
                header = requests.head(url, allow_redirects=True).headers
                if check and target != str(header.get(TYPE_KEY)).lower():
                    print(f"Didn't download {url}. Not {target}.")
                else:
                    self._download_target(header, url, fold)
            except GET_EXCEPT:
                pass

    def _download_target(self, header, url, folders):
        length_string = header.get(LENGTH_KEY, None)
        if length_string:
            content_length = float(length_string)
            if content_length and content_length <= self.max_size:
                self._download_file(url, folders)
            else:
                print(f"Didn't download {url}. Size exceeds {self.max_size}")

    def _download_file(self, url, fold):
        try:
            get_request = requests.get(url, allow_redirects=True)
            fname = Inventory._guess_filename(get_request, url)
            if fname:
                self._write_file(fname, fold, get_request)
            else:
                print(f"Didn't download {url}. Can't guess the filename.")
        except GET_EXCEPT:
            pass

    def _write_file(self, fname, fold, get_request, write_code="wb"):
        if self(fname):
            path = os.path.join(*fold, *wordsegment.segment(fname.lower()))
            os.makedirs(path, exist_ok=True)
            try:
                with open(os.path.join(path, fname), write_code) as target_file:
                    target_file.write(get_request.content)
            except OSError:
                pass

    def _next_node(self, lev, node, stem, ext, verb, fld, getrib="href"):
        nget = node.get(getrib)
        if nget:
            nget = nget.lower()
            if not any([skp in nget for skp in DO_NOT_GO_TO_PLACES_CONTAINING]):
                self._check_next_url(ext, fld, lev, nget, node, stem, verb)

    def _check_next_url(self, ext, fld, lev, nget, node, stem, verb):
        next_url = nget if nget.startswith('http') else f"{stem}/{nget}"
        fragment_counts = Tally()
        for fragment in next_url.split("/"):
            if fragment and len(fragment) > 1:
                fragment_counts[fragment] = 1
                if fragment_counts[fragment] > 2:
                    return False
        if any([nget.endswith(target) for target in ext]):
            self.fetch(next_url, fld)
        elif node.string:
            self._check_follow(fld, lev, next_url, nget, node, verb)
        return True

    def _check_follow(self, fld, lev, next_url, nget, node, verb):
        if (not any([nget.endswith(skip) for
                     skip in DO_NOT_GO_TO_PLACES_ENDING_IN])) and (
                not any([skip in next_url for skip in
                         DO_NOT_GO_TO_PLACES_CONTAINING])):
            if (not self.target_links) or (lev == 0) or (
                    (lev % self.max_between) != 0) or (
                    self.target_links in node.string.lower()):
                self.follow(next_url, fld, lev=lev + 1, verb=verb)

    @staticmethod
    def _guess_filename(get_request, url):
        if CONT_DISP in get_request.headers:
            return F_PAT.findall(get_request.headers[CONT_DISP])[0]
        return url.split("/")[-1]


if __name__ == "__main__":
    wordsegment.load()
    inv = Inventory()
    [inv.get_year(node) for top in TOP for node in BeautifulSoup(requests.get(
        top).text, 'html.parser').find_all('a') if node and node.string]
