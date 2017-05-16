# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#
#
#

"""This module contains type tuples and mappings derived from tmGrammar.
"""

import tmGrammar

# HACK: overload with missing attributes.
tmGrammar.ET = "ET"

# -----------------------------------------------------------------------------
#  Keys
# -----------------------------------------------------------------------------

kET = 'ET'
kCOUNT = 'COUNT'
kSeparator = '-'

# -----------------------------------------------------------------------------
#  Type tuples
# -----------------------------------------------------------------------------

ThresholdObjectTypes = (
    # Muon objects
    tmGrammar.MU,
    # Calorimeter objects
    tmGrammar.EG,
    tmGrammar.JET,
    tmGrammar.TAU,
    # Energy sums
    tmGrammar.ETM,
    tmGrammar.HTM,
    tmGrammar.ETT,
    tmGrammar.HTT,
    tmGrammar.ETTEM,
    tmGrammar.ETMHF,
)
"""Ordered list of ET threshold type object names."""

CountObjectTypes = (
    # Minimum Bias
    tmGrammar.MBT0HFP,
    tmGrammar.MBT1HFP,
    tmGrammar.MBT0HFM,
    tmGrammar.MBT1HFM,
    # Tower counts
    tmGrammar.TOWERCOUNT,
)
"""Ordered list of count type object names."""

ObjectTypes = ThresholdObjectTypes + CountObjectTypes
"""Ordered list of all supported threshold and count object types."""

ExternalObjectTypes = (
    tmGrammar.EXT,
)
"""Ordered list of supported external signal types."""

ObjectCutTypes = (
    tmGrammar.ETA,
    tmGrammar.PHI,
    tmGrammar.ISO,
    tmGrammar.QLTY,
    tmGrammar.CHG,
    tmGrammar.SLICE,
)
"""Orderd list of object cut type names."""

FunctionCutTypes = (
    tmGrammar.CHGCOR,
    tmGrammar.DETA,
    tmGrammar.DPHI,
    tmGrammar.DR,
    tmGrammar.MASS,
    tmGrammar.TBPT,
    tmGrammar.ORMDETA,
    tmGrammar.ORMDPHI,
    tmGrammar.ORMDR,
)
"""Orderd list of function cut type names."""

CutTypes = ObjectCutTypes + FunctionCutTypes
"""Ordered list of supported cut types."""

ThresholdCutNames = (
    kSeparator.join((tmGrammar.MU, tmGrammar.ET)),
    kSeparator.join((tmGrammar.EG, tmGrammar.ET)),
    kSeparator.join((tmGrammar.JET, tmGrammar.ET)),
    kSeparator.join((tmGrammar.TAU, tmGrammar.ET)),
    kSeparator.join((tmGrammar.ETM, tmGrammar.ET)),
    kSeparator.join((tmGrammar.HTM, tmGrammar.ET)),
    kSeparator.join((tmGrammar.ETT, tmGrammar.ET)),
    kSeparator.join((tmGrammar.HTT, tmGrammar.ET)),
    kSeparator.join((tmGrammar.ETTEM, tmGrammar.ET)),
    kSeparator.join((tmGrammar.ETMHF, tmGrammar.ET)),
)
"""Ordered list of threshold cut names."""

ObjectComparisonTypes = (
    tmGrammar.GE,
    tmGrammar.EQ,
)
"""Ordered list of supported object comparison types."""

FunctionTypes = (
    tmGrammar.comb,
    tmGrammar.dist,
    tmGrammar.mass_inv,
    tmGrammar.mass_trv,
    tmGrammar.comb_orm,
    tmGrammar.dist_orm,
    tmGrammar.mass_inv_orm,
)
"""Ordered list of functions."""

# -----------------------------------------------------------------------------
#  Mappings
# -----------------------------------------------------------------------------

ObjectScaleMap = {
    tmGrammar.MU: kET,
    tmGrammar.EG: kET,
    tmGrammar.TAU: kET,
    tmGrammar.JET: kET,
    tmGrammar.ETT: kET,
    tmGrammar.HTT: kET,
    tmGrammar.ETM: kET,
    tmGrammar.HTM: kET,
    tmGrammar.ETTEM: kET,
    tmGrammar.ETMHF: kET,
    tmGrammar.MBT0HFP: kCOUNT,
    tmGrammar.MBT1HFP: kCOUNT,
    tmGrammar.MBT0HFM: kCOUNT,
    tmGrammar.MBT1HFM: kCOUNT,
    tmGrammar.TOWERCOUNT: kCOUNT,
}
"""Mapping of threshold/count scale types for objects."""

FunctionCutsMap = {
    tmGrammar.comb: [tmGrammar.CHGCOR, tmGrammar.TBPT],
    tmGrammar.dist: [tmGrammar.DETA, tmGrammar.DPHI, tmGrammar.DR, tmGrammar.TBPT],
    tmGrammar.mass_inv: [tmGrammar.MASS, tmGrammar.DETA, tmGrammar.DPHI, tmGrammar.DR, tmGrammar.TBPT],
    tmGrammar.mass_trv: [tmGrammar.DETA, tmGrammar.DPHI, tmGrammar.DR, tmGrammar.TBPT],
    tmGrammar.comb_orm: [tmGrammar.ORMDETA, tmGrammar.ORMDPHI, tmGrammar.ORMDR, tmGrammar.TBPT],
    tmGrammar.dist_orm: [tmGrammar.ORMDETA, tmGrammar.ORMDPHI, tmGrammar.ORMDR, tmGrammar.DETA, tmGrammar.DPHI, tmGrammar.DR, tmGrammar.TBPT],
    tmGrammar.mass_inv_orm: [tmGrammar.MASS, tmGrammar.ORMDETA, tmGrammar.ORMDPHI, tmGrammar.ORMDR, tmGrammar.DETA, tmGrammar.DPHI, tmGrammar.DR, tmGrammar.TBPT],
}
"""Mapping function to cuts."""
