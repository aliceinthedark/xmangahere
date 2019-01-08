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

from typing import List, NoReturn

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow

def test() -> NoReturn:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

# def testViewer(paths: List[str]) -> NoReturn:
#     import sys
#     app = QApplication([])
#     window = ImageViewer(onExit=lambda: sys.exit(0))
#     window.show()
#     window.addImages(paths)
#     app.exec_()

if __name__ == '__main__':
    # import os
    # images = ['/home/andi/.xmanga/images/' + i for i in os.listdir('/home/andi/.xmanga/images')][:10]
    # testViewer(images)
    test()

