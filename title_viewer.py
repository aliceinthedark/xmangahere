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
from typing import List, NoReturn, Any

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


class TitleViewer(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._parent = parent

