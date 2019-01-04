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
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from base64 import b32encode

HOME_DIR = os.path.expanduser('~')
IMAGE_DIR = HOME_DIR + '/.xmanga/images/'

def get_saved_path(link: str) -> str:
    """
    Delete `token` and other parameters.
    """
    pure_link = link.split('?')[0]
    return IMAGE_DIR + b32encode(pure_link.encode('utf-8')).decode('utf-8') + '.jpg'

def load_image(link: str) -> str:
    """
    Download an image and return a file path to a cached one.
    """
    saved_path = get_saved_path(link)
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

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

images = [load_image(link) for link in sys.argv[1].split(' ') if link != '']

for path in images:
    print(path, sep='\n')
