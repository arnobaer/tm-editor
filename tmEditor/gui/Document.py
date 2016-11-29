# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

"""Document widget.
"""

# Trigger menu modules
import tmGrammar

from tmEditor.core import Toolbox
from tmEditor.core.Settings import MaxAlgorithms
from tmEditor.core import Menu
from tmEditor.core.Menu import Algorithm, Cut, Object, External, toObject
from tmEditor.core import XmlDecoder, XmlEncoder

# Models and proxies for table views
from tmEditor.gui.models import *
from tmEditor.gui.proxies import *
from tmEditor.gui.views import *

from tmEditor.gui.CutEditorDialog import CutEditorDialog
from tmEditor.gui.AlgorithmEditorDialog import AlgorithmEditorDialog
from tmEditor.gui.AlgorithmSelectIndexDialog import AlgorithmSelectIndexDialog, find_gaps, map_reserved, map_free # TODO
from tmEditor.gui.BottomWidget import BottomWidget

# Common widgets
from tmEditor.gui.CommonWidgets import IconLabel
from tmEditor.gui.CommonWidgets import SelectableLabel
from tmEditor.gui.CommonWidgets import TextFilterWidget
from tmEditor.gui.CommonWidgets import ReadOnlyLineEdit
from tmEditor.gui.CommonWidgets import RestrictedLineEdit
from tmEditor.gui.CommonWidgets import EtaCutChart, PhiCutChart

# Formatting
from tmEditor.core.Toolbox import fAlgorithm
from tmEditor.core.Toolbox import fCut
from tmEditor.core.Toolbox import fHex
from tmEditor.core.Toolbox import fThreshold
from tmEditor.core.Toolbox import fComparison
from tmEditor.core.Toolbox import fBxOffset

# Qt4 python bindings
from PyQt4 import QtCore
from PyQt4 import QtGui

import math
import logging
import copy
import sys, os

__all__ = ['Document', ]

# ------------------------------------------------------------------------------
#  Keys
# ------------------------------------------------------------------------------

kCable = 'cable'
kChannel = 'channel'
kData = 'data'
kDescription = 'description'
kExpression = 'expression'
kIndex = 'index'
kLabel = 'label'
kMaximum = 'maximum'
kMinimum = 'minimum'
kNBits = 'n_bits'
kName = 'name'
kNumber = 'number'
kObject = 'object'
kStep = 'step'
kSystem = 'system'
kType = 'type'

# ------------------------------------------------------------------------------
#  Document widget
# ------------------------------------------------------------------------------

class BaseDocument(QtGui.QWidget):
    """Document container widget used by MDI area."""

    modified = QtCore.pyqtSignal()
    """This signal is emitted whenever the content of the document changes."""

    def __init__(self, filename, parent=None):
        super(BaseDocument, self).__init__(parent)
        self.setFilename(filename)
        self.setModified(False)

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def filename(self):
        return self.__filename

    def setFilename(self, filename):
        self.__filename = os.path.abspath(filename)

    def isModified(self):
        return self.__modified

    def setModified(self, modified):
        self.__modified = bool(modified)

class Document(BaseDocument):
    """Menu document container widget used by MDI area.

    Document consists of pages listed in a tree view on the left. Adding pages
    requires assigning a top and a bottom widget to each page. Normally the top
    widget is either a generic table view or a more specific form widget whereas
    the bottom widget holds a versatile preview widget displaying details and
    actions for the above selected data set.

        +-----+-SlimSplitter-------+
        |     | +--SlimSplitter--+ |
        |     | | filterWidget   | |
        |     | +----------------+ |
        | [1] | | topStack       | |
        |     | +----------------+ |
        |     | | bottomWidget   | |
        |     | +----------------+ |
        +-----+--------------------+

        [1] navigationTreeWidget

    """

    def __init__(self, filename, parent=None):
        super(Document, self).__init__(filename, parent)
        # Attributes
        self.loadMenu(filename)
        # Layout
        self.setContentsMargins(0, 0, 0, 0)
        #
        self._pages = []
        # Filter bar
        self.filterWidget = TextFilterWidget(self, spacer=True)
        self.filterWidget.textChanged.connect(self.setFilterText)
        # Stacks
        self.topStack = QtGui.QStackedWidget(self)
        # Create table views.
        self.createNavigationTree()
        self.createBottomWidget()
        self.createMenuPage()
        self.createAlgorithmsPage()
        self.createCutsPage()
        self.createObjectsPage()
        self.createExternalsPage()
        self.createScalesPage()
        self.createScaleBinsPages()
        self.createExtSignalsPage()
        # Finsish navigation setup.
        self.navigationTreeWidget.expandItem(self.menuPage)
        self.navigationTreeWidget.setCurrentItem(self.menuPage)
        # Splitters
        self.vsplitter = SlimSplitter(QtCore.Qt.Horizontal, self)
        self.vsplitter.setObjectName("vsplitter")
        self.vsplitter.setStyleSheet("#vsplitter { border: 0; background: #888; }")
        self.vsplitter.addWidget(self.navigationTreeWidget)
        self.vsplitter.setOpaqueResize(False)
        self.hsplitter = SlimSplitter(QtCore.Qt.Vertical, self)
        self.hsplitter.addWidget(self.filterWidget)
        self.hsplitter.addWidget(self.topStack)
        self.hsplitter.addWidget(self.bottomWidget)
        self.vsplitter.addWidget(self.hsplitter)
        self.vsplitter.setStretchFactor(0, 0)
        self.vsplitter.setStretchFactor(1, 1)
        self.vsplitter.setSizes([200, 600])
        # Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.vsplitter)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def createNavigationTree(self):
        self.navigationTreeWidget = QtGui.QTreeWidget(self)
        self.navigationTreeWidget.headerItem().setHidden(True)
        self.navigationTreeWidget.setObjectName("navigationTreeWidget")
        self.navigationTreeWidget.setStyleSheet("#navigationTreeWidget { border: 0; background: #eee; }")
        self.navigationTreeWidget.itemSelectionChanged.connect(self.updateTop)

    def createBottomWidget(self):
        self.bottomWidget = BottomWidget(self)
        self.bottomWidget.toolbar.addTriggered.connect(self.addItem)
        self.bottomWidget.toolbar.editTriggered.connect(self.editItem)
        self.bottomWidget.toolbar.copyTriggered.connect(self.copyItem)
        self.bottomWidget.toolbar.removeTriggered.connect(self.removeItem)

    def createMenuPage(self):
        menuView = MenuWidget(self)
        menuView.loadMenu(self.menu())
        menuView.nameLineEdit.setText(self.menu().menu.name)
        menuView.commentTextEdit.setPlainText(self.menu().menu.comment)
        menuView.modified.connect(self.onModified)
        self.menuPage = self.addPage(self.tr("Menu"), menuView)

    def createAlgorithmsPage(self):
        model = AlgorithmsModel(self.menu(), self)
        tableView = self.newProxyTableView("algorithmsTableView", model)
        tableView.resizeColumnsToContents()
        self.algorithmsPage = self.addPage(self.tr("Algorithms"), tableView, self.menuPage)

    def createCutsPage(self):
        model = CutsModel(self.menu(), self)
        tableView = self.newProxyTableView("cutsTableView", model, proxyclass=CutsModelProxy)
        tableView.resizeColumnsToContents()
        self.cutsPage = self.addPage(self.tr("Cuts"), tableView, self.menuPage)

    def createObjectsPage(self):
        model = ObjectsModel(self.menu(), self)
        tableView = self.newProxyTableView("objectsTableView", model, proxyclass=ObjectsModelProxy)
        tableView.resizeColumnsToContents()
        self.objectsPage = self.addPage(self.tr("Object Requirements"), tableView, self.menuPage)

    def createExternalsPage(self):
        model = ExternalsModel(self.menu(), self)
        tableView = self.newProxyTableView("externalsTableView", model, proxyclass=ExternalsModelProxy)
        tableView.resizeColumnsToContents()
        self.externalsPage = self.addPage(self.tr("External Requirements"), tableView, self.menuPage)

    def createScalesPage(self):
        model = ScalesModel(self.menu(), self)
        tableView = self.newProxyTableView("scalesTableView", model, proxyclass=ScalesModelProxy)
        tableView.resizeColumnsToContents()
        self.scalesPage = self.addPage(self.tr("Scales"), tableView)

    def createExtSignalsPage(self):
        model = ExtSignalsModel(self.menu(), self)
        tableView = self.newProxyTableView("externalsTableView", model)
        tableView.resizeColumnsToContents()
        self.extSignalsPage = self.addPage(self.tr("External Signals"), tableView)

    def createScaleBinsPages(self):
        self.scalesTypePages = {}
        for scale in self.menu().scales.bins.keys():
            model = BinsModel(self.menu(), scale, self)
            tableView = self.newProxyTableView("{scale}TableView".format(**locals()), model)
            self.scalesTypePages[scale] = self.addPage(scale, tableView, self.scalesPage)

    def newProxyTableView(self, name, model, proxyclass=QtGui.QSortFilterProxyModel):
        """Factory to create new QTableView view using a QSortFilterProxyModel."""
        proxyModel = proxyclass(self)
        proxyModel.setFilterKeyColumn(-1)
        proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        proxyModel.setSourceModel(model)
        tableView = TableView(self)
        tableView.setObjectName(name)
        tableView.setStyleSheet(QtCore.QString("#%1 { border: 0; }").arg(name))
        tableView.setModel(proxyModel)
        tableView.doubleClicked.connect(self.editItem)
        tableView.selectionModel().selectionChanged.connect(self.updateBottom)
        return tableView

    def addPage(self, name, top=None, parent=None):
        """Add page consisting of navigation tree entry, top and bottom widget."""
        page = PageItem(name, top, self.bottomWidget, parent or self.navigationTreeWidget)
        if 0 > self.topStack.indexOf(top):
            self.topStack.addWidget(top)
        self._pages.append(page)
        return page

    def setFilterText(self, text):
        index, item = self.getSelection()
        excludedPages = [self.menuPage, ]
        if item not in excludedPages:
            item.top.model().setFilterFixedString(text)

    def onModified(self):
        self.setModified(True)
        self.modified.emit()

    def menu(self):
        return self._menu

    def loadMenu(self, filename):
        """Load menu from filename, setup new document."""
        self.setFilename(filename)
        self.setName(os.path.basename(filename))
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
        self._menu = queue.menu
        dialog.close()
        self.setModified(False)

    def saveMenu(self, filename=None):
        """Save menu to filename."""
        # Warn before loosing cuts
        orphans = self._menu.orphanedCuts()
        if len(orphans) > 1:
            QtGui.QMessageBox.information(self,
                self.tr("Found orphaned cuts"),
                QtCore.QString("There are %1 orphaned cuts (<em>%2</em>, ...) that will be lost as they can't be saved to the XML file!").arg(len(orphans)).arg(orphans[0])
            )
        elif len(orphans):
            QtGui.QMessageBox.information(self,
                self.tr("Found orphaned cut"),
                QtCore.QString("There is one orphaned cut (<em>%1</em>) that will be lost as it can't be saved to the XML file!").arg(orphans[0])
            )
        filename = filename or self.filename()
        self._menu.menu.name = str(self.menuPage.top.nameLineEdit.text())
        self._menu.menu.comment = str(self.menuPage.top.commentTextEdit.toPlainText())
        dialog = QtGui.QProgressDialog(self)
        dialog.setWindowTitle(self.tr("Saving..."))
        dialog.setCancelButton(None)
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.resize(260, dialog.height())
        dialog.show()
        QtGui.QApplication.processEvents()
        queue = XmlEncoder.XmlEncoderQueue(self._menu, filename)
        for callback in queue:
            dialog.setLabelText(self.tr("%1...").arg(queue.message().capitalize()))
            logging.debug("processing: %s...", queue.message())
            QtGui.QApplication.sendPostedEvents(dialog, 0)
            QtGui.QApplication.processEvents()
            callback()
            dialog.setValue(queue.progress())
            QtGui.QApplication.processEvents()
        dialog.close()
        self.setFilename(filename)
        self.setName(os.path.basename(filename))
        self.menuPage.top.loadMenu(self.menu())
        self.setModified(False)
        index, item = self.getSelection()
        item.top.update()
        self.updateBottom()

    def getSelection(self):
        items = self.navigationTreeWidget.selectedItems()
        if not len(items):
            return None, None
        item = items[0]
        if isinstance(item.top, QtGui.QTableView):
            index = item.top.currentMappedIndex()
            return index, item
        return None, item

    def getUnusedAlgorithmIndices(self):
        free = [i for i in range(MaxAlgorithms)]
        for algorithm in self.menu().algorithms:
            if int(algorithm.index) in free:
                free.remove(int(algorithm.index))
        return free

    def getUniqueAlgorithmName(self, basename="L1_Unnamed"):
        """Returns eiter *basename* if not already used in menu, else tries to
        find an unused basename with number suffix. Worst case returns just the
        basename.
        """
        name = basename
        if self.menu().algorithmByName(name):
            # Default name is already used, try to find a derivate
            for i in range(2, MaxAlgorithms):
                name = '{0}_{1}'.format(basename, i)
                if not self.menu().algorithmByName(name):
                    return name # got unused name!
        return basename # no clue...

    def updateTop(self):
        index, item = self.getSelection()
        if item and hasattr(item.top, 'sortByColumn'):
            item.top.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.topStack.setCurrentWidget(item.top)
        excludedPages = [self.menuPage, ]
        self.filterWidget.setEnabled(item not in excludedPages)
        self.filterWidget.setVisible(item not in excludedPages)
        self.filterWidget.filterLineEdit.setText("")
        self.setFilterText("")
        self.updateBottom()

    def updateBottom(self):
        index, item = self.getSelection()
        # Generic preview...
        if hasattr(item.bottom, 'reset'):
            item.bottom.reset()
        self.bottomWidget.show()
        if item is self.menuPage:
            lines = QtCore.QStringList()
            lines.append(self.tr("<p><strong>Scale Set:</strong> %1</p>").arg(self.menu().scales.scaleSet[kName]))
            lines.append(self.tr("<p><strong>External Signal Set:</strong> %1</p>").arg(self.menu().extSignals.extSignalSet[kName]))
            lines.append(self.tr("<p><strong>Menu UUID:</strong> %1</p>").arg(self.menu().menu.uuid_menu))
            lines.append(self.tr("<p><strong>Grammar Version:</strong> %1</p>").arg(self.menu().menu.grammar_version))
            item.bottom.setText(lines.join(""))
            item.bottom.toolbar.setButtonsEnabled(False)
        elif index and item and isinstance(item.top, TableView): # ignores menu view
            data = item.top.model().sourceModel().values[index.row()]
            rows = len(item.top.selectionModel().selectedRows())

            item.bottom.toolbar.setButtonsEnabled(True)

            if item is self.algorithmsPage:
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 algorithms.").arg(rows))
                else:
                    item.bottom.loadAlgorithm(data, self.menu())
            elif item is self.cutsPage:
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 cuts.").arg(rows))
                else:
                    item.bottom.loadCut(data)
            elif item is self.objectsPage:
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 object requirements.").arg(rows))
                else:
                    item.bottom.loadObject(data)
            elif item is self.externalsPage:
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 external signals.").arg(rows))
                else:
                    item.bottom.loadExternal(self.menu(), data)
            elif item is self.scalesPage:
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 scale sets.").arg(rows))
                else:
                    item.bottom.loadScale(data)
            elif item in self.scalesTypePages.values():
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 scale bins.").arg(rows))
                else:
                    item.bottom.loadScaleType(item.name, data)
            elif item is self.extSignalsPage:
                if 1 < rows:
                    item.bottom.setText(self.tr("Selected %1 external signals.").arg(rows))
                else:
                    item.bottom.loadSignal(data)
        else:
            item.bottom.reset()
            item.bottom.setText(self.tr("Nothing selected..."))
            item.bottom.toolbar.setButtonsEnabled(False)
        item.bottom.clearNotice()
        item.bottom.toolbar.hide()
        #item.bottom.setText("")
        if item is self.algorithmsPage:
            item.bottom.toolbar.show()
        elif item is self.cutsPage:
            # Experimental - enable only possible controls
            item.bottom.toolbar.show()
            item.bottom.toolbar.removeButton.setEnabled(False)
            if index:
                item.bottom.toolbar.removeButton.setEnabled(True)
                cut = self.menu().cuts[index.row()]
                for algorithm in self.menu().algorithms:
                    if cut.name in algorithm.cuts():
                        item.bottom.toolbar.removeButton.setEnabled(False)
        elif item is self.objectsPage:
            item.bottom.toolbar.hide()
            item.bottom.setNotice(self.tr("New objects requirements are created directly in the algorithm editor."), Toolbox.createIcon("info"))
        elif item is self.externalsPage:
            item.bottom.toolbar.hide()
            item.bottom.setNotice(self.tr("New external requirements are created directly in the algorithm editor."), Toolbox.createIcon("info"))
        else:
            item.bottom.toolbar.hide()

    def importCuts(self, cuts):
        """Import cuts from another menu, ignores if cut already present."""
        for cut in cuts:
            if not self.menu().cutByName(cut.name):
                self.menu().addCut(cut)
        self.cutsPage.top.model().setSourceModel(self.cutsPage.top.model().sourceModel())

    def importAlgorithms(self, algorithms):
        """Import algorithms from another menu."""
        for algorithm in algorithms:
            for cut in algorithm.cuts():
                if not self.menu().cutByName(cut):
                    raise RuntimeError(str(self.tr("Missing cut %1, unable to to import algorithm %2").arg(cut).arg(algorithm.name)))
            import_index = 0
            original_name = algorithm.name
            while self.menu().algorithmByName(algorithm.name):
                name = "{original_name}_import{import_index}".format(**locals())
                algorithm.name = name
                import_index += 1
            if import_index:
                QtGui.QMessageBox.information(self,
                    self.tr("Renamed algorithm"),
                    QtCore.QString("Renamed algorithm <em>%1</em> to <em>%2</em> as the name is already used.").arg(original_name).arg(algorithm.name)
                )
            if self.menu().algorithmByIndex(algorithm.index):
                index = self.getUnusedAlgorithmIndices()[0]
                QtGui.QMessageBox.information(self,
                    self.tr("Relocating algorithm"),
                    QtCore.QString("Moving algorithm <em>%1</em> from already used index %2 to free index %3.").arg(algorithm.name).arg(algorithm.index).arg(index),
                )
                algorithm.index = int(index)
            self.menu().addAlgorithm(algorithm)
            self.menu().extendReferenced(algorithm)
        self.algorithmsPage.top.model().setSourceModel(self.algorithmsPage.top.model().sourceModel())
        self.algorithmsPage.top.resizeColumnsToContents()
        self.objectsPage.top.model().setSourceModel(self.objectsPage.top.model().sourceModel())
        self.objectsPage.top.resizeColumnsToContents()

    def addItem(self):
        try:
            index, item = self.getSelection()
            if item is self.algorithmsPage:
                self.addAlgorithm(index, item)
            elif item is self.cutsPage:
                self.addCut(index, item)
        except RuntimeError, e:
            QtGui.QMessageBox.warning(self, self.tr("Error"), str(e))

    def addAlgorithm(self, index, item):
        dialog = AlgorithmEditorDialog(self.menu(), self)
        dialog.setModal(True)
        dialog.setIndex(self.getUnusedAlgorithmIndices()[0])
        dialog.setName(self.getUniqueAlgorithmName(str(self.tr("L1_Unnamed"))))
        dialog.editor.setModified(False)
        dialog.exec_()
        if dialog.result() != QtGui.QDialog.Accepted:
            return
        self.setModified(True)
        algorithm = Algorithm(
            int(dialog.index()),
            str(dialog.name()),
            str(dialog.expression()),
            str(dialog.comment())
        )
        for name in algorithm.cuts():
            if not filter(lambda item: item.name == name, self.menu().cuts):
                raise RuntimeError("NO SUCH CUT AVAILABLE")
        self.menu().addAlgorithm(algorithm)
        self.menu().extendReferenced(self.menu().algorithmByName(algorithm.name)) # IMPORTANT: add/update new objects!
        item.top.model().setSourceModel(item.top.model().sourceModel())
        self.algorithmsPage.top.resizeColumnsToContents()
        # REBUILD INDEX
        self.updateBottom()
        self.modified.emit()
        self.objectsPage.top.model().setSourceModel(self.objectsPage.top.model().sourceModel())
        self.objectsPage.top.resizeColumnsToContents()
        self.externalsPage.top.model().setSourceModel(self.externalsPage.top.model().sourceModel())
        self.externalsPage.top.resizeColumnsToContents()
        # Select new entry TODO: better to implement insertRow in model!
        proxy = item.top.model()
        for row in range(proxy.rowCount()):
            index = proxy.index(row, 1)
            if index.data().toPyObject() == algorithm.name:
                item.top.setCurrentIndex(index)
                break

    def addCut(self, index, item):
        dialog = CutEditorDialog(self.menu(), self)
        dialog.setModal(True)
        dialog.updateEntries()
        dialog.exec_()
        if dialog.result() != QtGui.QDialog.Accepted:
            return
        cut = dialog.newCut()
        self.menu().addCut(cut)
        self.cutsPage.top.model().setSourceModel(self.cutsPage.top.model().sourceModel())
        self.updateBottom()
        self.setModified(True)
        self.modified.emit()
        # Select new entry TODO: better to implement insertRow in model!
        proxy = item.top.model()
        for row in range(proxy.rowCount()):
            index = proxy.index(row, 0)
            if index.data().toPyObject() == cut.name:
                item.top.setCurrentIndex(index)
                break

    def editItem(self):
        try:
            index, item = self.getSelection()
            if item is self.algorithmsPage:
                self.editAlgorithm(index, item)
            elif item is self.cutsPage:
                self.editCut(index, item)
            self.updateBottom()
        except RuntimeError, e:
            QtGui.QMessageBox.warning(self, "Error", str(e))

    def editAlgorithm(self, index, item):
        algorithm = self.menu().algorithms[index.row()]
        dialog = AlgorithmEditorDialog(self.menu(), self)
        dialog.setModal(True)
        dialog.loadAlgorithm(algorithm)
        dialog.editor.setModified(False)
        dialog.exec_()
        if dialog.result() != QtGui.QDialog.Accepted:
            return
        self.setModified(True)
        dialog.updateAlgorithm(algorithm)
        for name in algorithm.cuts():
            if not filter(lambda item: item.name == name, self.menu().cuts):
                raise RuntimeError("NO SUCH CUT AVAILABLE") # TODO
        # REBUILD INDEX
        self.updateBottom()
        self.modified.emit()
        self.menu().extendReferenced(algorithm)
        self.objectsPage.top.model().setSourceModel(self.objectsPage.top.model().sourceModel())
        self.objectsPage.top.resizeColumnsToContents()
        self.externalsPage.top.model().setSourceModel(self.externalsPage.top.model().sourceModel())
        self.externalsPage.top.resizeColumnsToContents()

    def editCut(self, index, item):
        cut = self.menu().cuts[index.row()]
        dialog = CutEditorDialog(self.menu(), self)
        dialog.setModal(True)
        dialog.typeComboBox.setEnabled(False)
        dialog.loadCut(cut)
        dialog.exec_()
        if dialog.result() != QtGui.QDialog.Accepted:
            return
        self.setModified(True)
        dialog.updateCut(cut)
        self.updateBottom()
        self.modified.emit()

    def copyItem(self):
        index, item = self.getSelection()
        if item is self.algorithmsPage:
            self.copyAlgorithm(index, item)
        if item is self.cutsPage:
            self.copyCut(index, item)

    def copyAlgorithm(self, index, item):
        algorithm = copy.deepcopy(self.menu().algorithms[index.row()])
        dialog = AlgorithmEditorDialog(self.menu(), self)
        dialog.setModal(True)
        dialog.setIndex(self.getUnusedAlgorithmIndices()[0])
        dialog.setName(algorithm.name + "_copy")
        dialog.setExpression(algorithm.expression)
        dialog.editor.setModified(False)
        dialog.exec_()
        if dialog.result() != QtGui.QDialog.Accepted:
            return
        algorithm.expression = str(dialog.expression())
        algorithm.index = int(dialog.index())
        algorithm.name = str(dialog.name())
        for name in algorithm.cuts():
            if not filter(lambda item: item.name == name, self.menu().cuts):
                raise RuntimeError("NO SUCH CUT AVAILABLE") # TODO
        for name in algorithm.externals():
            if not filter(lambda item: item.name == name, self.menu().externals):
                raise RuntimeError("NO SUCH EXTERNAL AVAILABLE") # TODO
        self.menu().algorithms.append(algorithm)
        item.top.model().setSourceModel(item.top.model().sourceModel())
        self.objectsPage.top.model().setSourceModel(self.objectsPage.top.model().sourceModel())
        self.objectsPage.top.resizeColumnsToContents()
        self.externalsPage.top.model().setSourceModel(self.externalsPage.top.model().sourceModel())
        self.externalsPage.top.resizeColumnsToContents()
        # REBUILD INDEX
        self.updateBottom()
        self.modified.emit()
        self.setModified(True)
        for name in algorithm.objects():
            if not filter(lambda item: item.name == name, self.menu().objects):
                self.menu().addObject(toObject(name))
        self.objectsPage.top.model().setSourceModel(self.objectsPage.top.model().sourceModel())
        # Select new entry TODO: better to implement insertRow in model!
        proxy = item.top.model()
        for row in range(proxy.rowCount()):
            index = proxy.index(row, 1)
            if index.data().toPyObject() == algorithm.name:
                item.top.setCurrentIndex(index)
                break

    def copyCut(self, index, item):
        dialog = CutEditorDialog(self.menu(), self)
        dialog.setModal(True)
        dialog.loadCut(self.menu().cuts[index.row()])
        dialog.setSuffix('_'.join([dialog.suffix, 'copy']))
        dialog.suffixLineEdit.setEnabled(True) # todo
        dialog.exec_()
        if dialog.result() != QtGui.QDialog.Accepted:
            return
        cut = dialog.newCut()
        self.menu().addCut(cut)
        self.cutsPage.top.model().setSourceModel(self.cutsPage.top.model().sourceModel())
        self.updateBottom()
        self.setModified(True)
        self.modified.emit()
        # Select new entry TODO: better to implement insertRow in model!
        proxy = item.top.model()
        for row in range(proxy.rowCount()):
            index = proxy.index(row, 0)
            if index.data().toPyObject() == cut.name:
                item.top.setCurrentIndex(index)
                break

    def removeItem(self):
        index, item = self.getSelection()
        # Removing algorithm item
        if item is self.algorithmsPage:
            confirm = True
            while item.top.selectionModel().hasSelection():
                rows = item.top.selectionModel().selectedRows()
                row = rows[0]
                algorithm = item.top.model().sourceModel().values[item.top.model().mapToSource(row).row()]
                if confirm:
                    result = QtGui.QMessageBox.question(self, self.tr("Remove algorithm"),
                        self.tr("Do you want to remove algorithm <strong>%2, %1</strong> from the menu?").arg(algorithm.name).arg(algorithm.index),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.Abort if len(rows) > 1 else QtGui.QMessageBox.Yes | QtGui.QMessageBox.Abort)
                    if result == QtGui.QMessageBox.Abort:
                        break
                    elif result == QtGui.QMessageBox.YesToAll:
                        confirm = False
                item.top.model().removeRows(row.row(), 1)
            selection = item.top.selectionModel()
            selection.setCurrentIndex(selection.currentIndex(), QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
            # Removing orphaned objects.
            for name in self.menu().orphanedObjects():
                object = self.menu().objectByName(name)
                self.menu().objects.remove(object)
            self.objectsPage.top.model().setSourceModel(self.objectsPage.top.model().sourceModel())
            self.objectsPage.top.resizeColumnsToContents()
            self.externalsPage.top.model().setSourceModel(self.externalsPage.top.model().sourceModel())
            self.externalsPage.top.resizeColumnsToContents()
            # REBUILD INDEX
            self.updateBottom()
            self.modified.emit()
            self.setModified(True)

        # Removing cut item
        elif item is self.cutsPage:
            confirm = True
            while item.top.selectionModel().hasSelection():
                rows = item.top.selectionModel().selectedRows()
                row = rows[0]
                cut = item.top.model().sourceModel().values[item.top.model().mapToSource(row).row()]
                for algorithm in self.menu().algorithms:
                    if cut.name in algorithm.cuts():
                        QtGui.QMessageBox.warning(self, self.tr("Cut is used"),
                            self.tr("Cut %1 is used by algorithm %2 an can not be removed. Remove the corresponding algorithm first.").arg(cut.name).arg(algorithm.name),
                        )
                        return
                if confirm:
                    result = QtGui.QMessageBox.question(self, self.tr("Remove cut"),
                        self.tr("Do you want to remove cut <strong>%1</strong> from the menu?").arg(cut.name),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.Abort if len(rows) > 1 else QtGui.QMessageBox.Yes | QtGui.QMessageBox.Abort)
                    if result == QtGui.QMessageBox.Abort:
                        break
                    elif result == QtGui.QMessageBox.YesToAll:
                        confirm = False
                item.top.model().removeRows(row.row(), 1)
            selection = item.top.selectionModel()
            selection.setCurrentIndex(selection.currentIndex(), QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
            # REBUILD INDEX
            self.updateBottom()
            self.modified.emit()
            self.setModified(True)

# ------------------------------------------------------------------------------
#  Splitter and custom handle
# ------------------------------------------------------------------------------

class SlimSplitter(QtGui.QSplitter):
    """Slim splitter with a decent narrow splitter handle."""

    def __init__(self, orientation, parent=None):
        super(SlimSplitter, self).__init__(orientation, parent)
        self.setHandleWidth(1)
        self.setContentsMargins(0, 0, 0, 0)

    def createHandle(self):
        return SlimSplitterHandle(self.orientation(), self)

class SlimSplitterHandle(QtGui.QSplitterHandle):
    """Custom splitter handle for the slim splitter."""

    def __init__(self, orientation, parent=None):
        super(SlimSplitterHandle, self).__init__(orientation, parent)

    def paintEvent(self, event):
        pass

# ------------------------------------------------------------------------------
#  Navigation tree item
# ------------------------------------------------------------------------------

class PageItem(QtGui.QTreeWidgetItem):
    """Custom QTreeWidgetItem holding references to top and bottom widgets."""

    def __init__(self, name, top=None, bottom=None, parent=None):
        super(PageItem, self).__init__(parent, [name])
        self.name = name
        self.top = top
        self.bottom = bottom
        if not isinstance(parent, PageItem):
            # Hilight root items in bold text.
            font = self.font(0)
            font.setBold(True)
            self.setFont(0, font)

# ------------------------------------------------------------------------------
#  Menu information widget
# ------------------------------------------------------------------------------

class MenuWidget(QtGui.QScrollArea):
    """Menu information widget providing inputs for name and comment, shows
    assigned scale set."""

    modified = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MenuWidget, self).__init__(parent)
        self.nameLineEdit = RestrictedLineEdit(self)
        self.nameLineEdit.setPrefix("L1Menu_")
        self.nameLineEdit.setRegexPattern("L1Menu_[a-zA-Z0-9_]+")
        self.nameLineEdit.textEdited.connect(self.onModified)
        self.commentTextEdit = QtGui.QPlainTextEdit(self)
        self.commentTextEdit.setMaximumHeight(80)
        self.commentTextEdit.textChanged.connect(self.onModified)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(QtGui.QLabel(self.tr("Name"), self))
        vbox.addWidget(self.nameLineEdit)
        vbox.addWidget(QtGui.QLabel(self.tr("Comment"), self))
        vbox.addWidget(self.commentTextEdit)
        vbox.addItem(QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        view = QtGui.QWidget(self)
        view.setLayout(vbox)
        self.setAutoFillBackground(True)
        self.setWidgetResizable(True)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setWidget(view)

    def loadMenu(self, menu):
        """Load input values from menu."""
        self.nameLineEdit.setText(menu.menu.name)
        self.commentTextEdit.setPlainText(menu.menu.comment)

    def updateMenu(self, menu):
        """Update menu with values from inputs."""
        menu.menu.name = str(self.nameLineEdit.text())
        menu.menu.comment = str(self.commentTextEdit.toPlainText())

    def onModified(self):
        self.modified.emit()
