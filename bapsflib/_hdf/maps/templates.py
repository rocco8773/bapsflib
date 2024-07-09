"""
Module for the primary mapping template base class.
"""

__all__ = ["HDFMapTemplate", "MapTypes"]

import h5py
import os

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List


class MapTypes(Enum):
    # todo: come up with at better name...this should really be types
    #       for the different HDF5 structural elements
    DIGITIZER = 1
    CONTROL = 2
    MSI = 3


class HDFMapTemplate(ABC):
    """Template class for all mapping template classes."""

    _maptype = NotImplemented  # type: MapTypes

    def __init__(self, group: h5py.Group):
        """
        Parameters
        ----------
        group : `h5py.Group`
            The HDF5 to apply the mapping to.
        """

        # condition group arg
        if isinstance(group, h5py.Group):
            self._group = group
        else:
            raise TypeError(
                "Argument `group` is not of type h5py.Group, got type "
                f"{type(group)} instead."
            )

        # define _info attribute
        self._info = {
            "group name": os.path.basename(group.name),
            "group path": group.name,
        }

        # initialize configuration dictionary
        self._configs = {}

        # populate self.configs
        self._build_configs()

    @property
    def configs(self) -> Dict[str, Any]:
        """
        Dictionary containing all the gathered mapping information that
        is by `~bapsflib._hdf.utils.file.File` and its methods to
        provide a consistent user  interface.
        """
        return self._configs

    @property
    def dataset_names(self) -> List[str]:
        """
        List of names of the HDF5 datasets within the mapped group, at
        the root level.
        """
        dnames = [
            name for name in self.group if isinstance(self.group[name], h5py.Dataset)
        ]
        return dnames

    @property
    def group_name(self) -> str:
        """Name of the mapped HDF5 group."""
        return self._info["group name"]

    @property
    def group_path(self) -> str:
        """Path of the mapped HDF5 group in the HDF5 file."""
        return self._info["group path"]

    @property
    def group(self) -> h5py.Group:
        """Instance of the HDF5 group that was mapped."""
        return self._group

    @property
    def info(self) -> Dict[str, Any]:
        """
        Metadata information about the mapping type and the mapped group
        location in the HDF5 file.
        """
        return {**self._info, "maptype": self._maptype}

    @property
    def maptype(self) -> MapTypes:
        return self._maptype

    @property
    def subgroup_names(self) -> List[str]:
        """
        List of names of the HDF5 subgroups within the mapped group, at
        the root level.
        """
        sgroup_names = [
            name for name in self.group if isinstance(self.group[name], h5py.Group)
        ]
        return sgroup_names

    @abstractmethod
    def _build_configs(self):
        """
        Inspected the HDF5 group and build the configuration dictionary.
        Functionality should specifically populate ``self._configs``
        instead of `self.configs`.  If a mapping fails, then
        `bapsflib.utils.exceptions.HDFMappingError` should be raised.
        """
        ...