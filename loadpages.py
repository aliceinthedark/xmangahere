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

links = list(get_image_links())

# Save links in cache.
with open(CACHED_PATH, 'w') as f:
    f.write('\n'.join(links))

print('\n'.join(links), sep='')
