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

from typing import List, Dict, Callable, NoReturn, Any
from urllib.request import Request, urlopen

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QKeyEvent, QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCompleter,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QPushButton
)

from image_viewer import ImageViewer

IMAGE_WIDTH = 200
IMAGE_HEIGHT = 284

class ListItemWithTags(QListWidgetItem):

    def __init__(self, string: str, tags: Dict[str, Any] = {}):
        super().__init__(string)
        self.__tags = dict(tags)

    def tags(self) -> Dict[str, Any]:
        return self.__tags

class DetailsLoader(QObject):

    sig_done = pyqtSignal()

    def __init__(self, backEnd, title: str):
        super().__init__()
        self.__backEnd = backEnd
        self.__title = title
        self.__result = None

    @property
    def result(self):
        return self.__result

    @pyqtSlot()
    def work(self):
        self.__result = self.__backEnd.volumes(self.__title)
        self.sig_done.emit()


class ImageLoader(QObject):

    sig_done = pyqtSignal()

    def __init__(self, link: str):
        super().__init__()
        self.__link = link
        self.__result = None

    @property
    def result(self):
        return self.__result

    @pyqtSlot()
    def load(self) -> NoReturn:
        http_request = Request(
            self.__link,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        self.__result = urlopen(http_request).read()
        self.sig_done.emit()


class MangaDetailsWidget(QWidget):

    def __init__(self, titleLink: str, backEnd: object, parent: QWidget = None):
        super().__init__(parent=parent)
        self._parent = parent
        self.__title = titleLink
        self.__backEnd = backEnd
        #
        self.__createWidgets()
        self.__loadDetails()
        self.__createConnections()

    def __createWidgets(self) -> NoReturn:
        details = QWidget(self)
        detailsLayout = QHBoxLayout()
        # Image.
        self._image = QLabel()
        # Info.
        self._infoScroll = QScrollArea()
        info = QWidget(details)
        infoLayout = QVBoxLayout()
        infoLayout.addWidget(QLabel('Loading... Please, wait.'))
        info.setLayout(infoLayout)
        self._infoScroll.setWidget(info)
        self._infoScroll.setVisible(True)
        # All details.
        detailsLayout.addWidget(self._image)
        detailsLayout.addWidget(self._infoScroll)
        details.setLayout(detailsLayout)
        # Chapters.
        l = QVBoxLayout()
        self._optionList = QListWidget(parent=self)
        l.addWidget(details)
        l.addWidget(self._optionList)
        self.setLayout(l)
        #
        self._optionList.setFocus()

    def __loadDetails(self) -> NoReturn:
        self.__detailsLoader = DetailsLoader(self.__backEnd, self.__title)
        self.__thread = QThread()
        self.__detailsLoader.moveToThread(self.__thread)
        self.__detailsLoader.sig_done.connect(self.__updateView)
        self.__thread.started.connect(self.__detailsLoader.work)
        self.__thread.start()

    @pyqtSlot()
    def __updateView(self) -> NoReturn:
        result = self.__detailsLoader.result
        self.__loadCover(result['cover'])
        self.__updateInfo(result['info'])
        self.__updateChapterList(result['chapters'])

    def __loadCover(self, link: str) -> NoReturn:
        self.__coverLoader = ImageLoader(link)
        self.__thread2 = QThread()
        self.__coverLoader.moveToThread(self.__thread2)
        self.__coverLoader.sig_done.connect(self.__updateCover)
        self.__thread2.started.connect(self.__coverLoader.load)
        self.__thread2.start()

    @pyqtSlot()
    def __updateCover(self) -> NoReturn:
        data = self.__coverLoader.result
        image = QImage()
        image.loadFromData(data)
        self._image.setPixmap(QPixmap.fromImage(image).scaled(IMAGE_WIDTH, IMAGE_HEIGHT))

    def __updateInfo(self, info: Dict[str, str]) -> NoReturn:
        # Clean info.
        self._infoScroll.takeWidget()
        # Add items.
        infoW = QWidget(parent=self._infoScroll)
        infoLayout = QVBoxLayout()
        for k in info:
            if k != 'Summary':
                l = QLabel(k + ": " + info[k], parent=infoW)
                l.setMaximumWidth(self._infoScroll.size().width())
                infoLayout.addWidget(l)
            else:
                l = QLabel(k + ":\n" + info[k], parent=infoW)
                l.setWordWrap(True)
                l.setMaximumWidth(self._infoScroll.size().width())
                infoLayout.addWidget(l)
        infoW.setLayout(infoLayout)
        self._infoScroll.setWidget(infoW)
        self._infoScroll.setWidgetResizable(True)

    def __updateChapterList(self, chapters: List[Dict[str, str]]) -> NoReturn:
        self._optionList.clear()
        for ch in chapters:
            it = ListItemWithTags(ch['title'], tags=ch)
            self._optionList.addItem(it)

    def __createConnections(self) -> NoReturn:
        self._optionList.itemClicked.connect(self.__optionChosen)
        self._optionList.itemActivated.connect(self.__optionChosen)

    def keyPressEvent(self, keyEvent: QKeyEvent) -> NoReturn:
        if keyEvent.key() == Qt.Key_Escape:
            self._parent.goBack()
        elif not self._optionList.hasFocus():
            self._optionList.setFocus()
        # Idk why it doesn't select option list elements.
        super().keyPressEvent(keyEvent)

    def __optionChosen(self, item: QListWidgetItem) -> NoReturn:
        selectedVolume = item.tags()['link']
        self._parent.goTo(ImageViewer(selectedVolume, self.__backEnd, parent=self._parent))
