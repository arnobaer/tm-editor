# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

import tmGrammar

from tmEditor.core import Settings
from tmEditor.core.formatter import fCutValue, fCutData
from tmEditor.core.Algorithm import calculateDRRange
from tmEditor.core.Algorithm import calculateInvMassRange

from .AbstractTableModel import AbstractTableModel
# from tmEditor.gui.CommonWidgets import miniIcon

from tmEditor.PyQt5Proxy import QtCore, QtGui

__all__ = ['CutsModel', ]

def maximumCallback(item):
    """Custom infinite value getter."""
    if item.type == tmGrammar.MASS:
        minimum, maximum = calculateInvMassRange()
        if item.maximum >= maximum:
            return float('inf')
    return item.maximum

# ------------------------------------------------------------------------------
#  Cuts model class
# ------------------------------------------------------------------------------

class CutsModel(AbstractTableModel):
    """Default cuts table model."""

    def __init__(self, menu, parent = None):
        super(CutsModel, self).__init__(menu.cuts, parent)
        self.menu = menu
        self.addColumnSpec("Name", lambda item: item.name)
        self.addColumnSpec("Type", lambda item: item.type)
        self.addColumnSpec("Minimum", lambda item: item.minimum, fCutValue, self.AlignRight)
        self.addColumnSpec("Maximum", maximumCallback, fCutValue, self.AlignRight)
        self.addColumnSpec("Data", lambda item: fCutData(item))

    def data(self, index, role):
        """Overloaded for experimental icon decoration."""
        if index.isValid():
            if role == QtCore.Qt.FontRole:
                cut = self.values[index.row()]
                if cut.modified:
                    font = QtGui.QFont()
                    font.setWeight(QtGui.QFont.Bold)
                    return font
        return super(CutsModel, self).data(index, role)

    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.values.append(None)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            value = self.values[position + i]
            self.values.remove(value)
        self.endRemoveRows()
        return True
