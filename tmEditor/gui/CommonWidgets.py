# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

"""Commonly used helper widgets.

 * ColorIcon
 * ColorLabel
 * IconLabel
 * SelectableLabel

 * PrefixedSpinBox
 * ReadOnlyLineEdit
 * FilterLineEdit
 * ComboBoxPlus
 * RestrictedLineEdit
 * RestrictedPlainTextEdit
 * ListSpinBox

 * EtaCutChart
 * PhiCutChart
"""

from tmEditor.core import Toolbox

from PyQt4 import QtCore
from PyQt4 import QtGui

import math

__all__ = ['ColorIcon', 'ColorLabel', 'IconLabel', 'SelectableLabel',
           'PrefixedSpinBox', 'ReadOnlyLineEdit', 'FilterLineEdit',
           'ComboBoxPlus', 'RestrictedLineEdit', 'RestrictedPlainTextEdit',
           'ListSpinBox', 'EtaCutChart', 'PhiCutChart']

# -----------------------------------------------------------------------------
#  A framed color icon box.
# -----------------------------------------------------------------------------

class ColorIcon(QtGui.QFrame):
    """Provides an fixed sized framed color icon for building color labeled legends.

    The default square size is 12 pixel.
    """
    def __init__(self, color, parent=None, size=12):
        super(ColorIcon, self).__init__(parent)
        # Fix the icon size.
        self.setFixedSize(size, size)
        # Draw a border around the icon.
        self.setFrameShape(self.Box)
        self.setFrameShadow(self.Plain)
        # Make sure background color is displayed.
        self.setAutoFillBackground(True)
        # Store the icon's color.
        self.setColor(color)

    def setColor(self, color):
        # Store the icon's color.
        self.color = QtGui.QColor(color)
        # Setup the active color background brush.
        palette = self.palette()
        brush = QtGui.QBrush(self.color)
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush) # Bugfix for parent widgets with background role: Light.
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        self.setPalette(palette)

# -----------------------------------------------------------------------------
#  Legend label with color icon on the right.
# -----------------------------------------------------------------------------

class ColorLabel(QtGui.QWidget):
    """Color legend with icon and text label on the left."""

    def __init__(self, color, text, parent=None):
        super(ColorLabel, self).__init__(parent)
        # Create the icon and the text label.
        self.icon = ColorIcon(color, self)
        self.label = QtGui.QLabel(text, self)
        # Setup the layout.
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.icon)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def setColor(self, color):
        self.icon.setColor(color)

    def setText(self, text):
        self.label.setText(text)

# -----------------------------------------------------------------------------
#  Legend label with icon on the right.
# -----------------------------------------------------------------------------

class IconLabel(QtGui.QWidget):
    """label with 16x16 pixel icon and text label on the left."""

    def __init__(self, icon, text, parent=None):
        """Set icon of type QIcon and a text message."""
        super(IconLabel, self).__init__(parent)
        # Create the icon and the text label.
        self.icon = QtGui.QLabel(self)
        self.icon.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setIcon(icon)
        self.label = QtGui.QLabel(text, self)
        self.icon.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        # Setup the layout.
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.icon)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def setIcon(self, icon):
        """Set displayed icon."""
        self.icon.setPixmap(icon.pixmap(16, 16))

    def setText(self, text):
        """Set displayed text."""
        self.label.setText(str(text))

# -----------------------------------------------------------------------------
#  Selectable label.
# -----------------------------------------------------------------------------

class SelectableLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(SelectableLabel, self).__init__(parent)
        self.setWordWrap(True)
        self.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse |
            QtCore.Qt.TextSelectableByKeyboard |
            QtCore.Qt.TextSelectableByMouse
        )

# -----------------------------------------------------------------------------
#  Prefixed spin box
# -----------------------------------------------------------------------------

class PrefixedSpinBox(QtGui.QSpinBox):
    """A decimal spin box with plus and minus sign prefix.
    Used for assigning bunch crossing offsets.
    """
    def __init__(self, parent=None):
        """Constructur, takes optional reference to parent widget."""
        super(PrefixedSpinBox, self).__init__(parent)

    def textFromValue(self, value):
        return format(value, '+d') # prefix integers also with plus sign

# -----------------------------------------------------------------------------
#  Read only line edit widget.
# -----------------------------------------------------------------------------

class ReadOnlyLineEdit(QtGui.QLineEdit):
    """Customized rad only line edit."""

    def __init__(self, text, parent=None):
        """
        @param text the initial text to display.
        @param parent optional parent widget.
        """
        super(ReadOnlyLineEdit, self).__init__(str(text), parent)
        self.setReadOnly(True)
        # Set background to parent widget background.
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Window))
        self.setPalette(palette)

# -----------------------------------------------------------------------------
#  Filter line edit widget.
# -----------------------------------------------------------------------------

class FilterLineEdit(QtGui.QLineEdit):
    """Line edit with a clear button on the right side.
    Used for filter and search inputs.
    """
    def __init__(self, parent = None):
        """Constructur, takes optional reference to parent widget."""
        super(FilterLineEdit, self).__init__(parent)
        self._clearButton = QtGui.QToolButton(self)
        self._clearButton.setIcon(Toolbox.createIcon('edit-clear'))
        self._clearButton.setCursor(QtCore.Qt.ArrowCursor)
        self._clearButton.setStyleSheet("QToolButton { border: none; padding: 0; }")
        self._clearButton.hide()
        self._clearButton.clicked.connect(self.clear)
        self.textChanged.connect(self._updateClearButton)
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet(QtCore.QString("QLineEdit { padding-right: %1px; } ").arg(self._clearButton.sizeHint().width() + frameWidth + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(), self._clearButton.sizeHint().height() + frameWidth - 2),
                            max(msz.height(), self._clearButton.sizeHint().height() + frameWidth - 2))
    def resizeEvent(self, event):
        """Takes care of drawing the clear button on the right side."""
        sz = self._clearButton.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self._clearButton.move(self.rect().right() - frameWidth - sz.width(),
                              (self.rect().bottom() + 2 - sz.height()) / 2)
    def _updateClearButton(self, text):
        """Hide clear button when line edit contains no text."""
        self._clearButton.setVisible(not text.isEmpty())

# ------------------------------------------------------------------------------
#  Text filter widget
# ------------------------------------------------------------------------------

class TextFilterWidget(QtGui.QWidget):
    """Filter text input to be combined with a view. Optional enable a left
    *spacer* that justifies the content to the right."""

    textChanged = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, parent=None, spacer=False):
        super(TextFilterWidget, self).__init__(parent)
        self.setAutoFillBackground(True)
        self.filterLabel = QtGui.QLabel(self.tr("Filter"), self)
        self.filterLineEdit = FilterLineEdit(self)
        self.filterLineEdit.textChanged.connect(lambda text: self.textChanged.emit(text))
        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(10, 1, 1, 1)
        if spacer:
            hbox.addItem(QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum))
        hbox.addWidget(self.filterLabel)
        hbox.addWidget(self.filterLineEdit)
        self.setLayout(hbox)

# -----------------------------------------------------------------------------
#  Extended combo box widget.
# -----------------------------------------------------------------------------

class ComboBoxPlus(QtGui.QComboBox):
    """Enhanced combo box, permits to enable/disable items.
    >>> widget = ComboBoxPlus()
    >>> widget.insertItem(0, "sample")
    >>> widget.setItemEnabled(0, False)
    """

    def __init__(self, *args, **kwargs):
        super(ComboBoxPlus, self).__init__(*args, **kwargs)

    def setItemEnabled(self, index, enabled):
        """Enables or disables item at *index*."""
        # HACK:
        # see http://theworldwideinternet.blogspot.co.at/2011/01/disabling-qcombobox-items.html
        # and also https://forum.qt.io/topic/27419/qcombobox-item-disable
        modelIndex = self.model().index(index, 0)
        self.model().setData(modelIndex, QtCore.QVariant(33 if enabled else 0), QtCore.Qt.UserRole -1)

# -----------------------------------------------------------------------------
#  Restricted line edit widget.
# -----------------------------------------------------------------------------

class RestrictedLineEdit(QtGui.QLineEdit):
    """Restricted line edit widget.

    An optional prefix can be defined, it is part of the input but can not be
    edited or removed by the user. An optional regular expression prevents
    invalid user input (characters) also a maximum length of the full input
    can be defined.
    """

    def __init__(self, parent=None):
        """Widget's constructor.

        @param parent optional parent widget.
        """
        super(RestrictedLineEdit, self).__init__(parent)
        # Optional prefix.
        self._prefix = None
        # Optional regular expression pattern.
        self._pattern = None
        # Guard all user input changes.
        self.textChanged.connect(self.validate)

    def setPrefix(self, prefix):
        """Set a fixed value prefix."""
        self._prefix = str(prefix)
        self.validate()

    def prefix(self):
        """@returns prefix, None if not set."""
        return self._prefix

    def setRegexPattern(self, pattern):
        """Set regular expression pattern to guard user input."""
        self.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(str(pattern)), self))

    def validate(self):
        """Validate user input."""
        if self._prefix and self.text().length() < len(self._prefix):
            # Make it impossible to remove the L1Menu_ prefix.
            self.textChanged.disconnect()
            self.setText(self._prefix)
            self.textChanged.connect(self.validate)

# -----------------------------------------------------------------------------
#  Restricted plain text edit.
# -----------------------------------------------------------------------------

class RestrictedPlainTextEdit(QtGui.QPlainTextEdit):
    """Restricted plain text edit widget. Maximum length can be specified.
    """
    def __init__(self, parent=None):
        super(RestrictedPlainTextEdit, self).__init__(parent)
        self._maxLength = None
        self.textChanged.connect(self.validate)
        self.setTabChangesFocus(True)

    def setMaxLength(self, length):
        """Set maximal input length."""
        self._maxLength = int(length)

    def maxLength(self):
        """@returns maximal input length."""
        return int(self._maxLength)

    def validate(self):
        """Validate user input."""
        if self._maxLength:
            if self.toPlainText().length() > self._maxLength:
                self.textCursor().deletePreviousChar()

# -----------------------------------------------------------------------------
#  Custom integer list spin box
# -----------------------------------------------------------------------------

class ListSpinBox(QtGui.QSpinBox):
    """Custom spin box for a list of integers."""

    def __init__(self, values, parent=None):
        super(ListSpinBox, self).__init__(parent)
        self.setValues(values)

    def setValues(self, values):
        self.values = [int(value) for value in values]
        self.index = 0
        minimum = min(self.values)
        maximum = max(self.values)
        self.setRange(minimum, maximum)

    def stepBy(self, steps):
        self.index += steps
        self.setValue(int(self.values[self.index]))

    def value(self, index=None):
        """Returns bins floating point value by LUT index (upper or lower depending on mode)."""
        if index == None: index = self.index
        return self.values[index]

    def minimum(self):
        return self.value(0)

    def maximum(self):
        return self.value(-1)

    def setValue(self, value):
        value = self.nearest(value)
        super(ListSpinBox, self).setValue(value)

    def valueFromText(self, text):
        """Re-implementation of valueFromText(), it returns only the nearest."""
        return self.nearest(int(str(text).strip(" =<>!")))

    def nearest(self, value):
        """Returns nearest neighbor of value in range."""
        # See also "finding index of an item closest to the value in a list that's not entirely sorted"
        # http://stackoverflow.com/questions/9706041/finding-index-of-an-item-closest-to-the-value-in-a-list-thats-not-entirely-sort
        result = min(range(len(self.values)), key=lambda i: abs(self.values[i] - value))
        self.index = result
        return self.value(self.index)

#
# More complex widgets.
#

class EtaCutChart(QtGui.QWidget):
    """Graphical ETA cut representation."""

    Margin = 10
    Radius = 50
    Length = 100
    FontSize = 7

    def __init__(self, parent = None):
        """Constructur, takes optional reference to parent widget."""
        super(EtaCutChart, self).__init__(parent)
        self.setRange(-5, 5)
        self.setFixedSize(self.Margin * 2 + self.Length, self.Margin * 2 + self.Radius)

    def setRange(self, lower, upper):
        """Set lower and upper bounding of range."""
        self.lower = lower
        self.upper = upper

    def range(self):
        """Returns tuple containing lower and upper bounding of range."""
        return self.lower, self.upper

    def getPoint(self, value):
        """Calculate pixel coordinate for an ETA value."""
        stepX = (self.Length / 2) / 2.5
        stepY = self.Radius / 2.5
        if 2.5 < value <= 5.0:
            return QtCore.QPoint(self.Margin + self.Length, self.Margin + round(stepY * (value - 2.5)))
        if 0. < value <= 2.5:
            return QtCore.QPoint(self.Margin + self.Length / 2 + round(stepX * value), self.Margin)
        if -2.5 <= value <= 0.:
            return QtCore.QPoint(self.Margin + self.Length / 2 + round(stepX * value), self.Margin)
        if -5.0 <= value < -2.5:
            return QtCore.QPoint(self.Margin, self.Margin + abs(round(stepY * (value + 2.5))))
        raise ValueError()

    def paintEvent(self, event):
        """Paint ETA cut graph on windget."""
        lower, upper = self.range()
        painter = QtGui.QPainter(self)
        painter.setBrush(QtCore.Qt.white)
        # Draw Background
        painter.drawRect(self.Margin, self.Margin, self.Length, self.Radius)
        painter.setPen(QtGui.QPen(QtCore.Qt.transparent))
        painter.setBrush(QtCore.Qt.red)
        # Draw Polygon
        polygon = QtGui.QPolygon()
        polygon.append(QtCore.QPoint(self.Margin + self.Length / 2, self.Margin + self.Radius))
        polygon.append(self.getPoint(upper))
        if upper > 2.5 and lower < 2.5:
            polygon.append(QtCore.QPoint(self.Margin + self.Length, self.Margin))
        if lower < -2.5 and upper > -2.5:
            polygon.append(QtCore.QPoint(self.Margin, self.Margin))
        polygon.append(self.getPoint(lower))
        painter.drawPolygon(polygon)
        # Draw frames
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.setBrush(QtCore.Qt.transparent)
        painter.drawRect(self.Margin, self.Margin, self.Length / 2, self.Radius)
        painter.drawRect(self.Margin + self.Length / 2, self.Margin, self.Length / 2, self.Radius)
        painter.setFont(QtGui.QFont('Sans', self.FontSize))
        painter.drawText(QtCore.QPoint(self.Margin + self.Length / 2 - 2, self.Margin - 1), "0")
        painter.drawText(QtCore.QPoint(0, (self.Margin + self.Radius) + self.FontSize / 2), u"-5")
        painter.drawText(QtCore.QPoint(self.Margin + self.Length + 1, (self.Margin + self.Radius) + self.FontSize / 2), u"5")

class PhiCutChart(QtGui.QWidget):
    """Graphical PHI cut representation."""

    Margin = 8
    Radius = 30
    FontSize = 7

    def __init__(self, parent = None):
        """Constructur, takes optional reference to parent widget."""
        super(PhiCutChart, self).__init__(parent)
        self.setRange(0, 360 * 16)
        self.setFixedSize((self.Margin + self.Radius) * 2, (self.Margin + self.Radius) * 2)

    def setRange(self, lower, upper):
        """Set lower and upper bounding of range."""
        self.lower = lower
        self.upper = upper

    def range(self):
        """Returns tuple containing lower and upper bounding of range."""
        return self.lower, self.upper

    def paintEvent(self, event):
        """Paint PHI cut graph on windget."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rectangle = QtCore.QRect(self.Margin, self.Margin, self.Radius * 2, self.Radius * 2)
        painter.setPen(QtGui.QPen(QtCore.Qt.transparent))
        painter.setBrush(QtCore.Qt.white)
        painter.drawPie(rectangle, 0, 360 * 16)
        painter.setBrush(QtCore.Qt.red)
        lower, upper = self.range()
        lower = math.degrees(lower)
        upper = math.degrees(upper)
        if (lower < upper):
            painter.drawPie(rectangle, lower * 16, (upper-lower) * 16)
        else:
            painter.drawPie(rectangle, lower * 16, (360 - lower + upper) * 16)
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.setBrush(QtCore.Qt.transparent)
        painter.drawArc(rectangle, 0, 360 * 16)
        painter.setFont(QtGui.QFont('Sans', self.FontSize))
        painter.drawText(QtCore.QPoint(self.Radius * 2 + self.Margin + 2, (self.Margin + self.Radius) + self.FontSize / 2), u"0")
        painter.drawText(QtCore.QPoint(0, (self.Margin + self.Radius) + self.FontSize / 2), u"π")