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
# LICENSE for more details.
#

from typing import Iterator, Tuple, List, Dict, Any

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

def _get_titles(bs: Tag) -> Iterator[str]:
    for result in bs.find_all('div', {'class': 'result_search'})[0]:
        if type(result) is Tag and result.dt is not None:
            link = result.dt.a['href']
            title = result.dt.a.string
            yield link, title

def search(query: str) -> List[Dict[str, str]]:
    search_request = Request(
        'http://www.mangahere.cc/search.php?' + urlencode({'name': query}),
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    html_response = urlopen(search_request).read().decode('utf-8')
    bs = BS(html_response, 'html.parser')
    return [{'link': l, 'title': t} for l, t in _get_titles(bs)]

#
# Volumes.
#

def _get_cover_link(bs: Tag) -> str:
    top = bs.find_all('div', {'class': 'manga_detail_top'})[0]
    img = top.find_all('img', {'class': 'img'})[0]
    # 206x292
    return img['src']

def _get_details(bs: Tag) -> Dict[str, Any]:
    top = bs.find_all('div', {'class': 'manga_detail_top'})[0]
    info = {}
    def tag_is_valid(x: Tag) -> bool:
        return (type(x) is Tag and
            'class' not in x.attrs and #('class' in x and x['class'] != 'posR' or 'class' not in x) and \
            'id' not in x.attrs) #('id' in x and x['id'] != 'rate' or 'id' not in x)
    for li in top.find_all('ul', {'class': 'detail_topText'})[0].children:
        if tag_is_valid(li):
            label = li.label
            if label.h2 != None:
                label.h2.replace_with('')
            label = label.get_text().replace(':', '').strip()
            li.label.replace_with('')
            content = li.get_text().strip()
            info[label] = content
    return info

def _get_links(bs: Tag) -> Iterator[Dict[str, Any]]:
    for result in bs.find_all('div', {'class': 'detail_list'})[0].find_all('ul')[0]:
        # Results are <li> tags.
        if type(result) is Tag:
            span = result.find_all('span', {'class': 'left'})[0]
            if type(span) is Tag:
                link = span.a['href']
                title = span.a.string.replace('\n', '').strip()
                yield link, title

#@cached(domain='http://www.mangahere.cc/manga/')
def volumes(title: str) -> [str]:
    title = title if title.startswith('http') else 'http:' + title
    search_request = Request(
        title,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    html_response = urlopen(search_request).read().decode('utf-8')
    bs = BS(html_response, 'html.parser')
    #
    img = _get_cover_link(bs)
    info = _get_details(bs)
    chapters = [{'link': l, 'title': t} for l, t in _get_links(bs)]
    return {'cover': img, 'info': info, 'chapters': chapters}

#
# Page links.
#

def _extract_next_page_link(link: str) -> str:
    # link has a format of (as of 2019/01/03):
    # `//www.mangahere.cc/manga/title/`
    return link.replace('//www.mangahere.cc/manga/', '')

def _get_current_progress(bs: Tag) -> Tuple[int, int]:
    selector = bs.find_all('div', {'class': 'go_page clearfix'})[0].find_all('select')[1]
    current = selector.find_all('option', {'selected': 'selected'})[0].text
    last = [o for o in selector.children if type(o) is Tag and o.text != 'Featured'][-1].text
    return int(current), int(last)

def _get_image_link_and_next_page(bs: Tag) -> Tuple[str, str]:
    section = bs.find_all('section', {'id': 'viewer'})[0]
    if type(section) is not Tag:
        return None, 'javascript:void(0);'
    link = [x for x in section.children if x.name == 'a'][0]
    if type(link) is not Tag:
        return None, 'javascript:void(0);'
    page_link = link['href'] # _extract_next_page_link(link['href'])
    img_tag = link.find_all('img', {'id': 'image'})[0]
    img = img_tag['src'] if type(img_tag) is Tag else None
    return img_tag, page_link

def _get_image_links(page_link: str) -> Iterator[str]:
    progress_len = 0
    while page_link != 'javascript:void(0);':
        search_request = Request(
            #'http://www.mangahere.cc/manga/' + page_link,
            'http:' + page_link,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        html_response = urlopen(search_request).read().decode('utf-8')
        bs = BS(html_response, 'html.parser')
        #
        img, page_link = _get_image_link_and_next_page(bs)
        curr_p, all_p = _get_current_progress(bs)
        sys.stdout.write('\b' * progress_len)
        progress_len = sys.stdout.write("Progress: " + str(curr_p) + '/' + str(all_p))
        sys.stdout.flush()
        if img is not None:
            yield img['src']
    print('', sep='\n')



@preload_images
@cached(domain='http://www.mangahere.cc/manga/')
def pages(volume: str) -> [str]:
    return list(_get_image_links(volume))
