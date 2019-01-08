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

import sys
from typing import List, NoReturn

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QImageReader, QPixmap, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QCompleter,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QScrollArea,
    QPushButton
)

import mangahere
from cache import IMAGE_DIR

from search_widget import SearchWidget
from image_viewer import ImageViewer

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.__createWidgets()
        self.__createConnections()

    def __createWidgets(self):
        self._stack = QStackedWidget()
        #
        def goToViewer(chapter: str) -> NoReturn:
            print("Getting pages for " + chapter + "...")
            self.setWindowTitle(self.windowTitle() + chapter)
            pages = mangahere.pages(chapter)
            print('\n'.join(pages))
            print("Done.")
            viewer = ImageViewer()
            def back():
                self._stack.setCurrentIndex(2)
                self._stack.removeWidget(viewer)
            viewer._onExit = back
            self._stack.addWidget(viewer)
            self._stack.setCurrentIndex(3)
            viewer.addImages(pages)
        def goToChapters(title: str) -> NoReturn:
            print("Getting chapters for " + title + "...")
            self.setWindowTitle(title)
            chapters = mangahere.volumes(title)
            print("Got: " + ", ".join(chapters))
            w = SearchWidget(options=chapters, onSelect=goToViewer)
            def back() -> NoReturn:
                self._stack.setCurrentIndex(1)
                self._stack.removeWidget(w)
            w.onBack = back
            self._stack.addWidget(w)
            self._stack.setCurrentIndex(2)
        def goToTitles(queue: str) -> NoReturn:
            print("Searching for " + queue + "...")
            self.setWindowTitle("Search: " + queue)
            titles = mangahere.search(queue)
            print("Got: " + ", ".join(titles))
            w = SearchWidget(options=titles, onSelect=goToChapters)
            def back() -> NoReturn:
                self._stack.setCurrentIndex(0)
                self._stack.removeWidget(w)
            w.onBack = back
            self._stack.addWidget(w)
            self._stack.setCurrentIndex(1)
        self.setWindowTitle("Cute Manga")
        self._stack.addWidget(SearchWidget(onSelect=goToTitles, onBack=lambda: sys.exit(0)))
        #
        self.setCentralWidget(self._stack)

    def __createConnections(self):
        pass
