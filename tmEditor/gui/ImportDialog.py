# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

"""Import XML dialog.

This dialog provides an dialog to import algorithms from another XML file.

Example usage:
>>> dialog = ImportDialog()
>>> dialog.exec_()
>>> print dialog.algorithms
>>> print dialog.cuts
"""

from tmEditor.core import XmlDecoder
from tmEditor.core import Toolbox
from tmEditor.core.Settings import MaxAlgorithms

from tmEditor.gui.models import AlgorithmsModel
from tmEditor.gui.Document import TableView

# Common widgets
from tmEditor.gui.CommonWidgets import IconLabel

from PyQt4 import QtCore
from PyQt4 import QtGui

import logging

__all__ = ['ImportDialog', ]

# -----------------------------------------------------------------------------
#  Keys
# -----------------------------------------------------------------------------

kName = 'name'

# -----------------------------------------------------------------------------
#  Import dialog class
# -----------------------------------------------------------------------------

class ImportDialog(QtGui.QDialog):
    """Dialog providing importing of algorithms from another XML file."""

    def __init__(self, filename, menu, parent = None):
        super(ImportDialog, self).__init__(parent)
        # Algorithm selection
        self.algorithms = []
        self.cuts = []
        self.baseMenu = menu

        dialog = QtGui.QProgressDialog(self)
        dialog.setWindowTitle(self.tr("Loading..."))
        dialog.setCancelButton(None)
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.resize(260, dialog.height())
        dialog.show()
        QtGui.QApplication.processEvents()
        queue = XmlDecoder.XmlDecoderQueue(filename)
        for callback in queue:
            dialog.setLabelText(self.tr("%1...").arg(queue.message().capitalize()))
            logging.debug("processing: %s...", queue.message())
            QtGui.QApplication.sendPostedEvents(dialog, 0)
            QtGui.QApplication.processEvents()
            callback()
            dialog.setValue(queue.progress())
            QtGui.QApplication.processEvents()
        self.menu = queue.menu
        dialog.close()

        if self.menu.scales.scaleSet[kName] != self.baseMenu.scales.scaleSet[kName]:
            QtGui.QMessageBox.warning(self,
                self.tr("Different scale sets"),
                QtCore.QString("Unable to import from <em>%1</em> as scale sets do not match.").arg(filename),
            )
        # Important: sort out all duplicate algorithms !
        queue = []
        for algorithm in self.menu.algorithms:
            if self.baseMenu.algorithmByName(algorithm.name):
                queue.append(algorithm)
        for algorithm in queue:
            self.menu.algorithms.remove(algorithm)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.tr("Import"))
        self.setMinimumWidth(500)

        model = AlgorithmsModel(self.menu, self)
        proxyModel = QtGui.QSortFilterProxyModel(self)
        proxyModel.setSourceModel(model)
        self.tableView = TableView(self)
        self.tableView.setObjectName("importDialogTabelView")
        self.tableView.setStyleSheet("#importDialogTabelView { border: 0; }")
        self.tableView.setModel(proxyModel)
        self.tableView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        # Button box
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.importSelected)
        buttonBox.rejected.connect(self.reject)
        # Create layout.
        layout = QtGui.QGridLayout()
        layout.addWidget(self.tableView)
        layout.addWidget(IconLabel(Toolbox.createIcon("info"), self.tr("Select available algorithms to import."), self))
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def importSelected(self):
        """Import selected algorithms and auto adding new cuts."""
        for index in self.tableView.selectedIndexes():
            if index.column() == 0:
                # Use the assigned proxy model to map the index.
                #
                # CLEAN UP THE MESS
                index = self.tableView.model().mapToSource(index)
                algorithm = self.menu.algorithms[index.row()]
                self.algorithms.append(algorithm)
                for name in algorithm.cuts():
                    cut = self.menu.cutByName(name)
                    if cut not in self.cuts:
                        self.cuts.append(cut)
        self.accept()
