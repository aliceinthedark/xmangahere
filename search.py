#!/usr/bin/env python

import sys
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString, Tag
from urllib.request import Request, urlopen
from urllib.parse import urlencode

search_request = Request(
    'http://www.mangahere.cc/search.php?' + urlencode({'name': sys.argv[1]}),
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

html_response = urlopen(search_request).read().decode('utf-8')

bs = BS(html_response, 'html.parser')

def extract_title_from_link(link):
    # link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/title/`
    return link.split('/')[-2]

for result in bs.find_all('div', {'class': 'result_search'})[0]:
    if type(result) is not NavigableString and result.dt is not None:
        link = result.dt.a['href']
        print(extract_title_from_link(link))
