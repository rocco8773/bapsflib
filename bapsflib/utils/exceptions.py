# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017-2018 Erik T. Everson and contributors
#
# License: Standard 3-clause BSD; see "LICENSES/LICENSE.txt" for full
#   license terms and contributor agreement.
#
"""Exceptions specific to `bapsflib`."""
__all__ = [
    "BaPSFError",
    "HDFMappingError",
    "HDFReadControlError",
    "HDFReadDigiError",
    "HDFReadMSIError",
    "HDFReadError",
    "BaPSFWarning",
]

# -- CUSTOM EXCEPTIONS -----------------------------------------------------------


class BaPSFError(Exception):
    """
    Base class of BaPSF (bapsflib) custom errors.

    All custom exceptions raised by bapsflib should inherit from this
    class.
    """
    pass


class HDFMappingError(BaPSFError):
    """Exception for failed HDF5 mappings"""

    def __init__(self, device_name: str, why=""):
        super().__init__(f"'{device_name}' mapping failed: {why}")


class HDFReadError(BaPSFError):
    """Exception for failed HDF5 reading"""

    pass


class HDFReadDigiError(HDFReadError):
    """Exception for failed HDF5 reading of digitizer."""

    pass


class HDFReadControlError(HDFReadError):
    """Exception for failed HDF5 reading of digitizer."""

    pass


class HDFReadMSIError(HDFReadError):
    """Exception for failed HDF5 reading of digitizer."""

    pass

# -- CUSTOM WARNINGS -------------------------------------------------------------


class BaPSFWarning(Warning):
    """
    Base class of BaPSF (bapsflib) custom warnings.

    All custom warnings issued by bapsflib should inherit from this
    class.
    """
    pass
