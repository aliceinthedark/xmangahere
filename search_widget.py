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


class SearchWidget(QWidget):

    def __init__(self, options: List[str] = [], onSelect=lambda i: print(i), onBack=lambda: print('back')):
        super().__init__()
        self.options = options
        self.onSelect = onSelect
        self.onBack = onBack
        self.__createWidgets()
        self.__createConnections()

    def __createWidgets(self) -> NoReturn:
        bar = QWidget(self)
        barLayout = QHBoxLayout()
        comp = QCompleter(self.options)
        self.searchBar = QLineEdit(parent=self)
        self.searchBar.setCompleter(comp)
        self.searchButton = QPushButton("Go")
        barLayout.addWidget(self.searchBar)
        barLayout.addWidget(self.searchButton)
        bar.setLayout(barLayout)
        l = QVBoxLayout()
        self.optionList = QListWidget(parent=self)
        for item in self.options:
            self.optionList.addItem(item)
        l.addWidget(bar)
        l.addWidget(self.optionList)
        self.setLayout(l)
        self.searchBar.setFocus()

    def __createConnections(self) -> NoReturn:
        self.searchBar.textChanged.connect(self.__updateOptionList)
        self.searchBar.returnPressed.connect(self.__returnResult)
        self.searchButton.clicked.connect(self.__returnResult)
        self.optionList.itemClicked.connect(self.__optionClicked)
        self.optionList.itemActivated.connect(self.__optionClicked)

    def keyPressEvent(self, keyEvent: QKeyEvent) -> NoReturn:
        if keyEvent.key() == Qt.Key_Escape:
            self.onBack()
        elif self.searchBar.hasFocus():
            if keyEvent.key() == Qt.Key_Down:
                self.optionList.setFocus()
        elif self.optionList.hasFocus() and self.optionList.currentRow() == 0:
            if keyEvent.key() == Qt.Key_Up:
                self.searchBar.setFocus()
        super().keyPressEvent(keyEvent)

    def __updateOptionList(self) -> NoReturn:
        queue = self.searchBar.text()
        self.optionList.clear()
        for item in [i for i in self.options if i.startswith(queue)]:
            self.optionList.addItem(item)

    def __returnResult(self) -> NoReturn:
        queue = self.searchBar.text()
        self.onSelect(queue)

    def __optionClicked(self, item: QListWidgetItem) -> NoReturn:
        selectedText = item.text()
        self.searchBar.setText(selectedText)
        self.searchBar.setFocus()

