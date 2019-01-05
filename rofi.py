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

from subprocess import Popen, PIPE

def search_query() -> str:
    with Popen(['rofi', '-dmenu', '-lines', '0'], stdout=PIPE) as p:
        return p.stdout.read().decode('utf-8').replace('\n', '')

def select_title(titles: [str]) -> str:
    with Popen(['rofi', '-dmenu'], stdout=PIPE, stdin=PIPE) as menu:
        with menu.stdin:
            menu.stdin.write('\n'.join(titles).encode('utf-8'))
        return menu.stdout.read().decode('utf-8').replace('\n', '')

def select_volume(volumes: [str]) -> str:
    with Popen(['rofi', '-dmenu'], stdout=PIPE, stdin=PIPE) as menu:
        with menu.stdin:
            menu.stdin.write('\n'.join(volumes).encode('utf-8'))
        return menu.stdout.read().decode('utf-8').replace('\n', '')
