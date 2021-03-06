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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QCompleter,
    QListWidget,
    QListWidgetItem,
    QPushButton
)

from manga_details_widget import MangaDetailsWidget

class ListItemWithTags(QListWidgetItem):

    def __init__(self, string: str, tags: Dict[str, Any] = {}):
        super().__init__(string)
        self.__tags = dict(tags)

    def tags(self) -> Dict[str, Any]:
        return self.__tags


class SearchModel(object):

    def __init__(self, backEnd, listWidget: QListWidget):
        self.__backEnd = backEnd
        self.__list = listWidget

    @property
    def backEnd(self):
        return self.__backEnd

    def search(self, queue: str) -> NoReturn:
        results = self.__backEnd.search(queue)
        self.__list.clear()
        for res in results:
            it = ListItemWithTags(res['title'], tags=res)
            self.__list.addItem(it)


class SearchWidget(QWidget):

    def __init__(self, backEnd, parent: QWidget = None):
        super().__init__(parent)
        self._parent = parent
        self.__createWidgets()
        self._model = SearchModel(backEnd, self._optionList)
        self.__createConnections()

    def __createWidgets(self) -> NoReturn:
        bar = QWidget(self)
        barLayout = QHBoxLayout()
        self._searchBar = QLineEdit(parent=self)
        self._searchButton = QPushButton("Go")
        barLayout.addWidget(self._searchBar)
        barLayout.addWidget(self._searchButton)
        bar.setLayout(barLayout)
        #
        l = QVBoxLayout()
        self._optionList = QListWidget(parent=self)
        l.addWidget(bar)
        l.addWidget(self._optionList)
        self.setLayout(l)
        #
        self._searchBar.setFocus()

    def __createConnections(self) -> NoReturn:
        self._searchBar.returnPressed.connect(self.__returnResult)
        self._searchButton.clicked.connect(self.__returnResult)
        self._optionList.itemClicked.connect(self.__optionChosen)
        self._optionList.itemActivated.connect(self.__optionChosen)

    def keyPressEvent(self, keyEvent: QKeyEvent) -> NoReturn:
        if keyEvent.key() == Qt.Key_Escape:
            self._parent.goBack()
        elif self._searchBar.hasFocus():
            if keyEvent.key() == Qt.Key_Down:
                self._optionList.setFocus()
        elif self._optionList.hasFocus() and self._optionList.currentRow() == 0:
            if keyEvent.key() == Qt.Key_Up:
                self._searchBar.setFocus()
        super().keyPressEvent(keyEvent)

    def __returnResult(self) -> NoReturn:
        queue = self._searchBar.text()
        self._model.search(queue)

    def __optionChosen(self, item: QListWidgetItem) -> NoReturn:
        selectedTitle = item.tags()['link']
        self._parent.goTo(MangaDetailsWidget(selectedTitle, self._model.backEnd, parent=self._parent))
