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

import os
import os.path
import sys
from urllib.request import Request, urlopen
from base64 import b32decode, b32encode

from typing import NoReturn, Callable, List

XMANGA_DIR = os.path.expanduser('~') + '/.xmanga'
CACHE_DIR = XMANGA_DIR + '/cache/'
IMAGE_DIR = XMANGA_DIR + '/images/'
HISTORY_PATH = XMANGA_DIR + '/history'

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
if not os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, 'w') as f:
        f.write('')

def get_cached_path(link: str) -> str:
    return CACHE_DIR + b32encode(link.encode('utf-8')).decode('utf-8')

def get_image_path(link: str) -> str:
    """
    Delete `token` and other parameters.
    """
    pure_link = link.split('?')[0]
    return IMAGE_DIR + b32encode(pure_link.encode('utf-8')).decode('utf-8') + '.jpg'

def _exists(name: str) -> bool:
    cached_path = get_cached_path(name)
    return os.path.exists(cached_path)

def _get(name: str) -> [str]:
    cached_path = get_cached_path(name)
    if os.path.exists(cached_path):
        with open(cached_path) as f:
            return f.read().split('\n')
    else:
        raise Exception("Not cached object requested!")

def _put(name: str, to_be_cached: [str]) -> NoReturn:
    cached_path = get_cached_path(name)
    with open(cached_path, 'w') as f:
        return f.write('\n'.join(to_be_cached))

def cached(domain: str = '/common/'):
    def constructor(fun):
        def wrapper(name: str) -> [str]:
            link = domain + name + '/'
            if _exists(link):
                return _get(link)
            else:
                cache = fun(name)
                _put(link, cache)
                return cache
        return wrapper
    return constructor

def _load_image(link: str) -> str:
    """
    Download an image and return a file path to a cached one.
    """
    saved_path = get_image_path(link)
    if os.path.exists(saved_path):
        return saved_path
    http_request = Request(
        link,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    image = urlopen(http_request).read()
    # TODO! Check if downloaded successfully.
    with open(saved_path, 'wb') as f:
        f.write(image)
    return saved_path

def _save_images(links: [str]) -> [str]:
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    images = [_load_image(link) for link in links]
    return images

def preload_images(fun):
    def wrapper(links: List[str]) -> List[str]:
        return _save_images(fun(links))
    return wrapper

def _get_history(count: int) -> [str]:
    with open(HISTORY_PATH) as f:
        return [e for e in f.read().split('\n') if e != ''][:count]

def _save_history(history: [str], count: int) -> NoReturn:
    history = [e for e in list(set(history)) if e != '']
    with open(HISTORY_PATH, 'w') as f:
        def mark_hist(e: str) -> str:
            if e.startswith('-hist- '):
                return e
            else:
                return '-hist- ' + e
        f.write('\n'.join([mark_hist(x) for x in history[:count]]))

def save_history(count: int = 10):
    def constructor(fun):
        def wrapper():
            history = _get_history(count)
            req = fun(history)
            _save_history([req] + history, count)
            if req.startswith('-hist- '):
                req = req[len('-hist- '):]
            return req
        return wrapper
    return constructor
