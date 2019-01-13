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

from PyQt5.QtCore import Qt, QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QImage, QImageReader, QPixmap, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton
)


def _loadQtImage(path: str) -> QImage:
    reader = QImageReader(path)
    image = QImage(reader.read())
    if not image.isNull():
        return image
    else:
        return None


class ImageLoader(QObject):

    sig_done = pyqtSignal()

    def __init__(self, backEnd, volume: str):
        super().__init__()
        self.__backEnd = backEnd
        self.__volume = volume
        self.__result = None

    @property
    def result(self):
        return self.__result

    @pyqtSlot()
    def work(self):
        self.__result = self.__backEnd.pages(self.__volume)
        self.sig_done.emit()


class ImageViewer(QWidget):

    def __init__(self, volumeLink: str, backEnd, parent: QWidget = None):
        super().__init__(parent=parent)
        self._parent = parent
        self._images = []
        self._zoomRatio = 1
        self.__volumeLink = volumeLink
        self.__backEnd = backEnd
        #
        self._currentIndex = 0
        self.__createWidgets()
        self.__loadPages()
        self.__createConnections()

    def __createWidgets(self) -> NoReturn:
        self._bar = QWidget()
        barLayout = QHBoxLayout()
        self._nextButton = QPushButton(">")
        self._nextButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._prevButton = QPushButton("<")
        self._prevButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._zoomInButton = QPushButton("+")
        self._zoomInButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._zoomOutButton = QPushButton("-")
        self._zoomOutButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._progressLabel = QLabel("")
        self._bar.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        barLayout.addWidget(self._prevButton)
        barLayout.addWidget(self._nextButton)
        barLayout.addWidget(self._zoomOutButton)
        barLayout.addWidget(self._zoomInButton)
        barLayout.addWidget(self._progressLabel)
        self._bar.setLayout(barLayout)
        #
        l = QVBoxLayout()
        self._scroll = QScrollArea()
        self._image = QLabel(parent=self._scroll)
        self._image.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self._image.setScaledContents(True)
        self._scroll.setWidget(self._image)
        self._scroll.setVisible(False)
        self._scroll.setWidgetResizable(True)
        #
        l.addWidget(self._bar)
        l.addWidget(self._scroll)
        self.setLayout(l)

    def __loadPages(self) -> NoReturn:
        self.__imageLoader = ImageLoader(self.__backEnd, self.__volumeLink)
        self.__thread = QThread()
        self.__imageLoader.moveToThread(self.__thread)
        self.__imageLoader.sig_done.connect(self.__updatePages)
        self.__thread.started.connect(self.__imageLoader.work)
        self.__thread.start()

    @pyqtSlot()
    def __updatePages(self):
        results = self.__imageLoader.result
        self.addImages(results)

    def __createConnections(self) -> NoReturn:
        self._nextButton.setFocusProxy(self)
        self._prevButton.setFocusProxy(self)
        self._zoomInButton.setFocusProxy(self)
        self._zoomOutButton.setFocusProxy(self)
        self._scroll.setFocusProxy(self)
        self._image.setFocusProxy(self)
        #
        self._nextButton.clicked.connect(self.__nextButtonClicked)
        self._prevButton.clicked.connect(self.__prevButtonClicked)
        self._zoomInButton.clicked.connect(self.__zoomIn)
        self._zoomOutButton.clicked.connect(self.__zoomOut)

    def keyPressEvent(self, keyEvent: QKeyEvent) -> NoReturn:
        if keyEvent.key() == Qt.Key_Right or keyEvent.key() == Qt.Key_N:
            self.__nextButtonClicked()
        elif keyEvent.key() == Qt.Key_Left or keyEvent.key() == Qt.Key_P:
            self.__prevButtonClicked()
        elif keyEvent.key() == Qt.Key_Plus or keyEvent.key() == Qt.Key_Equal:
            self.__zoomIn()
        elif keyEvent.key() == Qt.Key_Minus:
            self.__zoomOut()
        elif keyEvent.key() == Qt.Key_Q or keyEvent.key() == Qt.Key_Escape:
            self._parent.goBack()
        elif keyEvent.key() == Qt.Key_J:
            sb = self._scroll.verticalScrollBar()
            sb.setValue(sb.value() + 30)
        elif keyEvent.key() == Qt.Key_K:
            sb = self._scroll.verticalScrollBar()
            sb.setValue(sb.value() - 30)
        elif keyEvent.key() == Qt.Key_L:
            sb = self._scroll.horizontalScrollBar()
            sb.setValue(sb.value() + 30)
        elif keyEvent.key() == Qt.Key_H:
            sb = self._scroll.horizontalScrollBar()
            sb.setValue(sb.value() - 30)
        super().keyPressEvent(keyEvent)

    def resizeEvent(self, event: QResizeEvent) -> NoReturn:
        self.__resizeImage()
        super().resizeEvent(event)

    def __nextButtonClicked(self) -> NoReturn:
        if len(self._images) == 0:
            print("[Warning] Images not loaded!")
            return
        if self._currentIndex + 1 >= len(self._images):
            self._currentIndex = 0
        else:
            self._currentIndex += 1
        self.__setImage(self._currentIndex)

    def __prevButtonClicked(self) -> NoReturn:
        if len(self._images) == 0:
            print("[Warning] Images not loaded!")
            return
        if self._currentIndex - 1 < 0:
            self._currentIndex = len(self._images) - 1
        else:
            self._currentIndex -= 1
        self.__setImage(self._currentIndex)

    def __setImage(self, index: int) -> NoReturn:
        if index < 0 or index >= len(self._images):
            raise Exception("Image index is out of boundaries!")
        self._currentIndex = index
        self.__resizeImage()
        self.__showProgress()

    def __zoomIn(self) -> NoReturn:
        print("Zooming in")
        self._zoomRatio *= 1.25
        self.__resizeImage()

    def __zoomOut(self) -> NoReturn:
        print("Zooming out")
        self._zoomRatio *= 0.8
        self.__resizeImage()

    def __resizeImage(self) -> NoReturn:
        if len(self._images) == 0:
            print("[Warning] Images not loaded!")
            return
        pixmap = QPixmap.fromImage(self._images[self._currentIndex])
        if self._zoomRatio != 1:
            pixmap = pixmap.scaled(self._zoomRatio * self.size(), aspectRatioMode=Qt.KeepAspectRatio)
        self._image.setPixmap(pixmap)
        self._scroll.setVisible(True)
        self._image.adjustSize()

    def __showProgress(self) -> NoReturn:
        if len(self._images) == 0:
            self._progressLabel.setText("No images")
        else:
            self._progressLabel.setText(str(self._currentIndex + 1) + "/" + str(len(self._images)))

    def addImages(self, paths: List[str]) -> NoReturn:
        images = [_loadQtImage(p) for p in paths]
        images = [i for i in images if i is not None]
        print("Loaded " + str(len(images)) + " images.")
        self._images.extend(images)
        if len(self._images) > 0:
            self.__setImage(0)
        else:
            self.__showProgress()
