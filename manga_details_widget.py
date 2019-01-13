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

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCompleter,
    QListWidget,
    QListWidgetItem,
    QPushButton
)

from image_viewer import ImageViewer

class ListItemWithTags(QListWidgetItem):

    def __init__(self, string: str, tags: Dict[str, Any] = {}):
        super().__init__(string)
        self.__tags = dict(tags)

    def tags(self) -> Dict[str, Any]:
        return self.__tags

class VolumesLoader(QObject):

    sig_done = pyqtSignal()

    def __init__(self, backEnd, title):
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


class DetailModel(QObject):

    def __init__(self, title, backEnd, listWidget: QListWidget):
        super().__init__()
        self.__backEnd = backEnd
        self.__list = listWidget
        self.__title = title
        self.__worker = VolumesLoader(backEnd, title)
        self.__thread = QThread()
        self.__thread.setObjectName('thread_' + str(hash(self.__worker)))
        self.__worker.moveToThread(self.__thread)
        self.__worker.sig_done.connect(self.__updateView)
        self.__thread.started.connect(self.__worker.work)
        self.__thread.start()

    @pyqtSlot()
    def __updateView(self) -> NoReturn:
        self.__list.clear()
        for res in self.__worker.result:
            it = ListItemWithTags(res['title'], tags=res)
            self.__list.addItem(it)

    @property
    def backEnd(self):
        return self.__backEnd


class MangaDetailsWidget(QWidget):

    def __init__(self, titleLink: str, backEnd, parent: QWidget = None):
        super().__init__(parent=parent)
        self._parent = parent
        self.__title = titleLink
        self.__createWidgets()
        self._model = DetailModel(titleLink, backEnd, self._optionList)
        self.__createConnections()

    def __createWidgets(self) -> NoReturn:
        bar = QWidget(self)
        barLayout = QHBoxLayout()
        # TODO! Add details.
        barLayout.addWidget(QLabel("Details are not available in this version."))
        bar.setLayout(barLayout)
        #
        l = QVBoxLayout()
        self._optionList = QListWidget(parent=self)
        l.addWidget(bar)
        l.addWidget(self._optionList)
        self.setLayout(l)
        #
        self._optionList.setFocus()

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
        self._parent.goTo(ImageViewer(selectedVolume, self._model.backEnd, parent=self._parent))
