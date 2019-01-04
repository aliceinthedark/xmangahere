#!/usr/bin/env python
#
# This file is part of xmangahere project.
#
# Copyright (C) 2019 aliceinthedark <don't @ me>
# All Rights Reserved
# 
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# LICENSE.md for more details.
#

import os
import os.path
import sys
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString, Tag
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from base64 import b32decode, b32encode

def get_cached_path(link: str) -> str:
    return CACHE_DIR + b32encode(link.encode('utf-8')).decode('utf-8')

HOME_DIR = os.path.expanduser('~')
CACHE_DIR = HOME_DIR + '/.xmanga/cache/'
LINK = 'http://www.mangahere.cc/manga/' + sys.argv[1] + '/'
CACHED_PATH = get_cached_path(LINK)

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Print cached data if already saved.
if os.path.exists(CACHED_PATH):
    with open(CACHED_PATH) as f:
        sys.stdout.write(f.read())
        sys.stdout.flush()
    sys.exit(0)

search_request = Request(
    LINK,
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

html_response = urlopen(search_request).read().decode('utf-8')

bs = BS(html_response, 'html.parser')

def extract_title_from_link(link: str) -> str:
    # Link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/<useful data>`
    return link.replace('//www.mangahere.cc/manga/', '')

def get_links():
    for result in bs.find_all('div', {'class': 'detail_list'})[0].find_all('ul')[0]:
        # Results are <li> tags.
        if type(result) is not NavigableString:
            span = result.find_all('span', {'class': 'left'})[0]
            if type(span) is not NavigableString:
                link = span.a['href']
                yield extract_title_from_link(link)

# Save links in cache.
links = list(get_links())
with open(CACHED_PATH, 'w') as f:
    f.write('\n'.join(links))

for link in links:
    print(link, sep='\n')
