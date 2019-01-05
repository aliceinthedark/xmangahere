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

from typing import Generator

import os
import os.path
import sys
from bs4 import BeautifulSoup as BS
from bs4 import Tag
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from base64 import b32decode, b32encode

from cache import cached, preload_images

#
# Search.
#

def _extract_title_from_link(link: str) -> str:
    # link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/title/`
    return link.split('/')[-2]

def _get_titles(bs: Tag) -> Generator:
    for result in bs.find_all('div', {'class': 'result_search'})[0]:
        if type(result) is Tag and result.dt is not None:
            link = result.dt.a['href']
            yield _extract_title_from_link(link)

def search(query: str) -> [str]:
    search_request = Request(
        'http://www.mangahere.cc/search.php?' + urlencode({'name': query}),
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    html_response = urlopen(search_request).read().decode('utf-8')
    bs = BS(html_response, 'html.parser')
    return list(_get_titles(bs))

#
# Volumes.
#

def _extract_title_from_link(link: str) -> str:
    # Link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/<useful data>`
    return link.replace('//www.mangahere.cc/manga/', '')

def _get_links(bs: Tag):
    for result in bs.find_all('div', {'class': 'detail_list'})[0].find_all('ul')[0]:
        # Results are <li> tags.
        if type(result) is Tag:
            span = result.find_all('span', {'class': 'left'})[0]
            if type(span) is Tag:
                link = span.a['href']
                yield _extract_title_from_link(link)

@cached(domain='http://www.mangahere.cc/manga/')
def volumes(title: str) -> [str]:
    search_request = Request(
        'http://www.mangahere.cc/manga/' + title,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    html_response = urlopen(search_request).read().decode('utf-8')
    bs = BS(html_response, 'html.parser')
    # Save links in cache.
    return list(_get_links(bs))

#
# Page links.
#

def _extract_next_page_link(link: str) -> str:
    # link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/title/`
    return link.replace('//www.mangahere.cc/manga/', '')

def _get_image_links(page_link: str) -> Generator:
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
        page_link = _extract_next_page_link(link['href'])
        img = link.find_all('img', {'id': 'image'})[0]
        if type(img) is Tag:
            yield img['src']

@preload_images
@cached(domain='http://www.mangahere.cc/manga/')
def pages(volume: str) -> [str]:
    return list(_get_image_links(volume))
