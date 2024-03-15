from main import Inventory

import requests
import wordsegment

from bs4 import BeautifulSoup

VICTORIA_TOP = r"https://www.vec.vic.gov.au/results/state-election-results"
WEST_AUS_TOP = r"https://www.elections.wa.gov.au/elections/state"
SOUTH_AUS_TOP = r"https://www.ecsa.sa.gov.au/elections"
NSW_TOP = r"https://elections.nsw.gov.au/elections/"
NORTH_TER_TOP = r"https://ntec.nt.gov.au/elections"
TASMANIA_TOP = r"https://www.tec.tas.gov.au/"
ACT_TOP = r"https://www.elections.act.gov.au/"
QLD_TOP = r"https://www.ecq.qld.gov.au/elections/election-results"

TOP_PAGES = {
    "victoria": (VICTORIA_TOP, ),
    "tasmania": (TASMANIA_TOP, ),
    "south_australia": (SOUTH_AUS_TOP, ),
    "nsw": (NSW_TOP, ),
    "northern_territory": (NORTH_TER_TOP, ),
    "act": (ACT_TOP, ),
    "queensland": (QLD_TOP, ),
    "west_australia": (WEST_AUS_TOP, ),
             }


if __name__ == "__main__":
    wordsegment.load()
    inv = Inventory(target=None, between=None, depth=6)
    [inv.follow(node.get('href'), ('state', directory_name), ) for
     directory_name, state_pages in TOP_PAGES.items() for top in state_pages
        for node in
     BeautifulSoup(requests.get(top).text, 'html.parser').find_all('a')]


