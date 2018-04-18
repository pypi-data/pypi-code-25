#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .qt import QtWidgets
from .settings import NODES_VIEW_SETTINGS
from .local_config import LocalConfig


class NodesDockWidget(QtWidgets.QDockWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = LocalConfig.instance().loadSectionSettings("NodesView", NODES_VIEW_SETTINGS)

    def _filterTextChangedSlot(self, text):
        self.parent().uiNodesView.setCurrentSearch(text)
        self.parent().uiNodesView.refresh()

    def _filterIndexChangedSlot(self, index):
        self._settings["nodes_view_filter"] = index
        LocalConfig.instance().saveSectionSettings("NodesView", self._settings)

        if index == 0:
            self.parent().uiNodesView.setShowInstalledAppliances(True)
            self.parent().uiNodesView.setShowBuiltinAvailableAppliances(True)
            self.parent().uiNodesView.setShowMyAvailableAppliances(True)
        elif index == 1:
            self.parent().uiNodesView.setShowInstalledAppliances(True)
            self.parent().uiNodesView.setShowBuiltinAvailableAppliances(False)
            self.parent().uiNodesView.setShowMyAvailableAppliances(False)
        elif index == 2:
            self.parent().uiNodesView.setShowInstalledAppliances(False)
            self.parent().uiNodesView.setShowBuiltinAvailableAppliances(True)
            self.parent().uiNodesView.setShowMyAvailableAppliances(True)
        else:
            self.parent().uiNodesView.setShowInstalledAppliances(False)
            self.parent().uiNodesView.setShowBuiltinAvailableAppliances(False)
            self.parent().uiNodesView.setShowMyAvailableAppliances(True)
        self.parent().uiNodesView.refresh()

    def populateNodesView(self, category):
        if self.parent().uiNodesFilterComboBox.currentIndex() != self._settings["nodes_view_filter"]:
            self.parent().uiNodesFilterComboBox.setCurrentIndex(self._settings["nodes_view_filter"])
            self._filterIndexChangedSlot(self._settings["nodes_view_filter"])
        self.parent().uiNodesFilterComboBox.activated.connect(self._filterIndexChangedSlot)
        self.parent().uiNodesFilterLineEdit.textChanged.connect(self._filterTextChangedSlot)
        self.parent().uiNodesView.clear()
        text = self.parent().uiNodesFilterLineEdit.text().strip().lower()
        self.parent().uiNodesView.populateNodesView(category, text)
