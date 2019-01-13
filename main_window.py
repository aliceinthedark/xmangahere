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
from typing import List, Dict, NoReturn, Any

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
from title_viewer import TitleViewer
from image_viewer import ImageViewer

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._widgetList = [SearchWidget, TitleViewer, ImageViewer]
        self.__createWidgets()

    def __createWidgets(self):
        self._stack = QStackedWidget()
        #
        self.setWindowTitle("Cute Manga")
        self._stack.addWidget(SearchWidget(parent=self, backEnd=mangahere))
        #
        self.setCentralWidget(self._stack)

    def goBack(self) -> NoReturn:
        ci = self._stack.currentIndex()
        if ci == 0:
            sys.exit(0)
        else:
            cw = self._stack.currentWidget()
            self._stack.setCurrentIndex(ci - 1)
            self._stack.removeWidget(cw)

    def goTo(self, widget: QWidget) -> NoReturn:
        ci = self._stack.currentIndex()
        self._stack.addWidget(widget)
        self._stack.setCurrentIndex(ci + 1)
