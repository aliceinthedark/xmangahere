#!/usr/bin/env python

import sys
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString, Tag
from urllib.request import Request, urlopen
from urllib.parse import urlencode

search_request = Request(
    'http://www.mangahere.cc/manga/' + sys.argv[1] + '/',
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

html_response = urlopen(search_request).read().decode('utf-8')

bs = BS(html_response, 'html.parser')

def extract_title_from_link(link: str) -> str:
    # Link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/title/`
    return link.replace('//www.mangahere.cc/manga/', '')

for result in bs.find_all('div', {'class': 'detail_list'})[0].find_all('ul')[0]:
    # Results are <li> tags.
    if type(result) is not NavigableString:
        span = result.find_all('span', {'class': 'left'})[0]
        if type(span) is not NavigableString:
            link = span.a['href']
            print(extract_title_from_link(link))
