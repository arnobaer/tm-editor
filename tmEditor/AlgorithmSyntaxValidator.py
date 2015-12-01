# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

"""Algorithm syntax validator class.

Usage example
-------------

>>> validator = AlgorithmSyntaxValidator(menu)
>>> validator.validate(expression)

"""

import tmGrammar

from tmEditor.Menu import (
    isOperator,
    isObject,
    isCut,
    isFunction,
    functionObjects,
    functionCuts,
    functionObjectsCuts,
    objectCuts,
)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

__all__ = ['AlgorithmSyntaxValidator', 'AlgorithmSyntaxError']

# -----------------------------------------------------------------------------
#  Base classes
# -----------------------------------------------------------------------------

class SyntaxValidator(object):
    """Base class to be inherited by custom syntax validator classes."""

    def __init__(self, menu):
        self.menu = menu # menu handle
        self.rules = []

    def validate(self, expression):
        for rule in self.rules:
            rule.validate(expression)

    def addRule(self, cls):
        """Add a syntx rule class. Creates and tores an instance of the class."""
        self.rules.append(cls(self))

class SyntaxRule(object):
    """Base class to be inherited by custom syntax rule classes."""

    def __init__(self, validator):
        self.validator = validator

    def tokens(self, expression):
        """Parses algorithm expression and returns list of tokens."""
        tmGrammar.Algorithm_Logic.clear()
        if not tmGrammar.Algorithm_parser(expression):
            raise AlgorithmSyntaxError("Failed to parse algorithm expression `{expression}'".format(**locals()))
        return tmGrammar.Algorithm_Logic.getTokens()

    def validate(self, expression):
        raise NotImplementedError()

# -----------------------------------------------------------------------------
#  Algorithm language specific classes
# -----------------------------------------------------------------------------

class AlgorithmSyntaxError(Exception):
    """Exeption for algoithm syntax errors thrown by class AlgorithmSyntaxValidator."""
    token = None

class AlgorithmSyntaxValidator(SyntaxValidator):
    """Algorithm syntax validator class."""

    def __init__(self, menu):
        super(AlgorithmSyntaxValidator, self).__init__(menu)
        self.addRule(CombBxOffset)
        self.addRule(DistNrObjects)
        self.addRule(DistDeltaEtaRange)

class CombBxOffset(SyntaxRule):
    """Validates that all objects of a combination function use the same BX offset."""

    def validate(self, expression):
        for token in self.tokens(expression):
            if not isFunction(token):
                continue
            if not token.startswith(tmGrammar.comb):
                continue
            f = tmGrammar.Function_Item()
            if not tmGrammar.Function_parser(token, f):
                raise AlgorithmSyntaxError(f.message)
            objects = functionObjects(token)
            for i in range(len(objects)):
                if int(objects[i].bx_offset) != int(objects[0].bx_offset):
                    e = AlgorithmSyntaxError("All object requirements of function comb{{...}} must be of same bunch crossing offset.\n" \
                                               "Invalid expression near \"{token}\"".format(**locals()))
                    e.token = token
                    raise e

class DistNrObjects(SyntaxRule):
    """Limit number of objects for distance function."""

    def validate(self, expression):
        for token in self.tokens(expression):
            if not isFunction(token):
                continue
            if not token.startswith(tmGrammar.dist):
                continue
            f = tmGrammar.Function_Item()
            if not tmGrammar.Function_parser(token, f):
                raise AlgorithmSyntaxError(str(f.message))
            objects = functionObjects(token)
            if len(objects) != 2:
                raise AlgorithmSyntaxError("Function dist{{...}} requires excactly two object requirements.\n" \
                                           "Invalid expression near \"{token}\"".format(**locals()))

class DistDeltaEtaRange(SyntaxRule):
    """Validates that delta-eta cut ranges does not exceed assigned objects limits."""

    def validate(self, expression):
        menu = self.validator.menu
        for token in self.tokens(expression):
            if not isFunction(token):
                continue
            if not token.startswith(tmGrammar.dist):
                continue
            for name in functionCuts(token):
                cut = menu.cutByName(name)
                if cut.type == tmGrammar.DETA:
                    for object in functionObjects(token):
                        scale = filter(lambda scale: scale['object']==object.type and scale['type']=='ETA', menu.scales.scales)[0]
                        minimum = 0
                        maximum = abs(float(scale['minimum'])) + float(scale['maximum'])
                        if not (minimum <= float(cut.minimum) <= maximum):
                            raise AlgorithmSyntaxError("Cut \"{name}\" minimum limit of {cut.minimum} exceed valid object DETA range of {minimum}".format(**locals()))
                        if not (minimum <= float(cut.maximum) <= maximum):
                            raise AlgorithmSyntaxError("Cut \"{name}\" maximum limit of {cut.maximum} exceed valid object DETA range of {maximum}".format(**locals()))
                if cut.type == tmGrammar.DPHI:
                    for object in functionObjects(token):
                        scale = filter(lambda scale: scale['object']==object.type and scale['type']=='PHI', menu.scales.scales)[0]
                        minimum = 0
                        maximum = float(scale['maximum']) / 2.
                        if not (minimum <= float(cut.minimum) <= maximum):
                            raise AlgorithmSyntaxError("Cut \"{name}\" minimum limit of {cut.minimum} exceed valid object DPHI range of {minimum}".format(**locals()))
                        if not (minimum <= float(cut.maximum) <= maximum):
                            raise AlgorithmSyntaxError("Cut \"{name}\" maximum limit of {cut.maximum} exceed valid object DPHI range of {maximum}".format(**locals()))
