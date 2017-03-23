# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

import tmGrammar

# HACK: overload with missing attributes.
tmGrammar.ET = "ET"
tmGrammar.PT = "PT"

from tmEditor.core.formatter import fCutValue
from .AbstractTableModel import AbstractTableModel

from tmEditor.PyQt5Proxy import QtCore
from tmEditor.PyQt5Proxy import QtGui

__all__ = ['ScalesModel', ]

# ------------------------------------------------------------------------------
#  Keys
# ------------------------------------------------------------------------------

kObject = 'object'
kType = 'type'
kMinimum = 'minimum'
kMaximum = 'maximum'
kStep = 'step'
kNBits = 'n_bits'

def fPatchType(item):
    """Patch muon type from ET to PT."""
    if item[kType] == tmGrammar.ET:
        if item[kObject] == tmGrammar.MU:
            return tmGrammar.PT
    return item[kType]

# ------------------------------------------------------------------------------
#  Scales model class
# ------------------------------------------------------------------------------

class ScalesModel(AbstractTableModel):
    """Default scales table model."""

    def __init__(self, menu, parent = None):
        super(ScalesModel, self).__init__(menu.scales.scales, parent)
        self.addColumnSpec("Object", lambda item: item[kObject])
        self.addColumnSpec("Type", fPatchType)
        self.addColumnSpec("Minimum", lambda item: item[kMinimum], fCutValue, self.AlignRight)
        self.addColumnSpec("Maximum", lambda item: item[kMaximum], fCutValue, self.AlignRight)
        self.addColumnSpec("Step", lambda item: item[kStep], fCutValue, self.AlignRight)
        self.addColumnSpec("Bitwidth", lambda item: item[kNBits], int, self.AlignRight)
        self.addEmptyColumn()
