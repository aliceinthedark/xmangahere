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
from base64 import b32decode, b32encode

from cache import CACHE_DIR, get_image_path

def search(_query) -> [str]:
    cached = [b32decode(x.encode('utf-8')).decode('utf-8') for x in os.listdir(CACHE_DIR)]
    cached_with_l = [(len([y for y in x.split('/') if y != '']), x) for x in cached]
    titles = [t for (l, t) in cached_with_l if l == 4]
    return titles

def volumes(title: str) -> [str]:
    cached = [b32decode(x.encode('utf-8')).decode('utf-8') for x in os.listdir(CACHE_DIR)]
    cached_with_l = [(len([y for y in x.split('/') if y != '']), x) for x in cached]
    volumes = [t for (l, t) in cached_with_l if l > 4]
    matching = [x for x in volumes if x.startswith(title[:-1])]
    return matching

def pages(volume: str) -> [str]:
    with open(CACHE_DIR + b32encode(volume.encode('utf-8')).decode('utf-8')) as links:
        return [get_image_path(x) for x in links.read().split('\n')]
    
