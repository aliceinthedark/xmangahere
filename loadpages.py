#!/usr/bin/env python

# a_bias_girl/v01/c004/

import sys
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString, Tag
from urllib.request import Request, urlopen
from urllib.parse import urlencode

def extract_next_page_link(link: str) -> str:
    # link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/title/`
    return link.replace('//www.mangahere.cc/manga/', '')

def get_image_links():
    page_link = sys.argv[1]
    while page_link != 'javascript:void(0);':
        search_request = Request(
            'http://www.mangahere.cc/manga/' + page_link,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        html_response = urlopen(search_request).read().decode('utf-8')
        bs = BS(html_response, 'html.parser')
        #
        section = bs.find_all('section', {'id': 'viewer'})[0]
        if type(section) is not Tag:
            break
        link = [x for x in section.children if x.name == 'a'][0]
        if type(link) is not Tag:
            break
        page_link = extract_next_page_link(link['href'])
        img = link.find_all('img', {'id': 'image'})[0]
        if type(img) is Tag:
            yield img['src']

for link in get_image_links():
    print(link)
