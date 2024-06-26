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
"""Module for the template digitizer mappers."""
__all__ = ["HDFMapDigiTemplate"]

import copy
import h5py
import os

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union
from warnings import warn

from bapsflib.utils.warnings import HDFMappingWarning


class HDFMapDigiTemplate(ABC):
    # noinspection PySingleQuotedDocstring
    '''
    Template class for all digitizer mapping classes to inherit from.

    Any inheriting class should define :code:`__init__` as::

        def __init__(self, group: h5py.Group)
            """
            :param group: HDF5 group object
            """
            # initialize
            HDFMapDigiTemplate.__init__(self, group)

            # define device adc's
            self._device_adcs = ()  # type: Tuple[str, ...]

            # populate self.configs
            self._build_configs()

    .. note::

        * In the code sample above, :code:`self._device_adcs` is
          digitizer specific and should be defined as a tuple of
          strings of analog-digital-converter (adc) names.
        * Any method that raises a :exc:`NotImplementedError` is
          intended to be overwritten by the inheriting class.
    '''

    def __init__(self, group: h5py.Group):
        """
        :param group: the digitizer HDF5 group
        """
        # condition group arg
        if isinstance(group, h5py.Group):
            self._digi_group = group
        else:
            raise TypeError("arg `group` is not of type h5py.Group")

        # define _info attribute
        self._info = {
            "group name": os.path.basename(group.name),
            "group path": group.name,
        }

        # define device adc's
        self._device_adcs = ()

        # initialize configuration dictionary
        self._configs = {}

    @abstractmethod
    def _build_configs(self):
        """
        Examines the HDF5 group to build the :data:`configs` dictionary.

        :raise: :exc:`NotImplementedError`

        .. note::

            It is recommended to define additioal helper methods to
            construct and populate the :attr:`configs` dictionary.

            .. csv-table:: Possible helper methods.
                :header: "Method", "Description"
                :widths: 20, 60

                ":meth:`_adc_info_first_pass`", "
                Build the tuple of tuples containing the adc connected
                board and channels numbers, as well as, the associated
                setup configuration for each connected board.
                "
                ":meth:`_adc_info_second_pass`", "
                Review and update the adc tuple generated by
                :meth:`_adc_info_first_pass`.  Here, the expected
                datasets can be checked for existence and the setup
                dictionary can be append with any additional entries.
                "
                ":meth:`_find_active_adcs`", "
                Examine the configuration group to determine which
                digitizer adc's were used for the configuration.
                "
                ":meth:`_find_adc_connections`", "
                Used to determine the adc's connected board and
                channels.  It can also act as the seed for
                :meth:`_adc_info_first_pass`.
                "
                ":meth:`_parse_config_name`", "
                Parse the configuration group name to determine the
                digitizer configuration name.
                "

        """
        raise NotImplementedError

    @property
    def active_configs(self) -> List[str]:
        """List of active digitizer configurations"""
        active = []
        for cname in self.configs:
            if self.configs[cname]["active"]:
                active.append(cname)

        return active

    @property
    def configs(self) -> dict:
        """
        Dictionary containing al the relevant mapping information to
        translate the HDF5 data into a numpy array by
        :class:`~bapsflib._hdf.utils.hdfreaddata.HDFReadData`.

        **-- Constructing** :code:`configs` **--**

        The :code:`configs` dict is a nested dictionary where the first
        level of keys represents the digitizer configuration names.
        Each configuration dictionary then consists of a set of
        non-polymorphic and polymorphic keys.  Any additional keys are
        currently ignored.  The non-polymorphic keys are as follows:

        .. csv-table:: Required Non-Polymorphic keys for
                       :code:`config=configs['config name']`
            :header: "Key", "Description"
            :widths: 20, 60

            "::

                config['active']
            ", "
            :code:`True` or :code:`False` indicating if this
            configuration was used in recording the digitizer datasets
            "
            "::

                config['adc']
            ", "
            Tuple of strings naming the adc's used for this
            configuration. For example, ::

                ('SIS 3301', )
            "
            "::

                config['config group path']
            ", "
            Internal HDF5 path to the digitizer configuration group.
            For example, ::

                '/foo/bar/SIS 3301/Configuration: first_run'
            "
            "::

                config['shotnum']
            ", "
            Dictionary defining how the digitzier shot numbers are
            recorded.  It is assumed, the shot numbers are recorded in
            the header dataset associated with the main dataset.  The
            dictionary should look like, ::

                config['shotnum'] = {
                    'dset field': ('Shot number',),
                    'shape': (),
                    'dtype': numpy.uint32,
                }

            where :code:`'dset field'` is the field name of the
            header dataset containing shot numbers, :code:`'shape'` is
            the numpy shape of the shot number data, and :code:`'dtype'`
            is the numpy :code:`dtype` of the data.  This all defines
            the numpy :code:`dtype` of the :code:`'shotnum'` field in
            the
            :class:`~bapsflib._hdf.utils.hdfreaddata.HDFReadData`
            constructed numpy array.
            "

        The required polymorphic keys are the names of each adc listed
        in :code:`configs['config name']['adc']`.  These entries contain
        the adc board and channel hookup configuration, as well as, the
        adc setup configuration for each connected board.  Continuing
        with the example above, this key would look something like ::

            >>> type(config['SIS 3301'])
            tuple
            >>> type(config['SIS 3301'][0])
            tuple
            >>> len(config['SIS 3301'][0])
            3

        where each nested tuple represents one board connection to the
        adc and is 3 elements long.  The breakdown of the nested tuple
        follows:

        .. csv-table:: Breakdown of Polymorphic Key.
                       (:code:`config=configs['config name']`)
            :header: "Key", "Description"
            :widths: 20, 60

            "::

                config['SIS 3301'][0][0]
            ", "
            :code:`int` representing the connected board number
            "
            "::

                config['SIS 3301'][0][1]
            ", "
            :code:`Tuple[int, ...]` representing the connected channel
            numbers associated with the board number
            "
            "::

                config['SIS 3301'][0][2]
            ", "
            :code:`Dict[str, Any]` representing the setup configuration
            of the adc.  The dictionary should look like::

                config['SIS 3301'][0][2] = {
                    'bit: 10,
                    'clock rate':
                        astropy.units.Quantity(100.0, unit='MHz'),
                    'nshotnum': 10,
                    'nt': 10000,
                    'sample average (hardware)': None,
                    'shot average (software)': None,
                }

            where :code:`'bit'` represents the bit resolution of the
            adc, :code:`'clock rate'` represents the base clock rate of
            the adc, :code:`'nshotnum'` is the number of shot numbers
            recorded, :code:`'nt'` is the number of time samples
            recorded, :code:`'sample average (hardware)'` is the number
            of time samples averaged together (this and the
            :code:`'clock rate'` make up the :code:`'sample rate'`),
            and :code:`'shot average (software)'` is the number of shots
            intended to be average together.
            "

        """
        return self._configs

    @abstractmethod
    def construct_dataset_name(
        self, board: int, channel: int, config_name=None, adc=None, return_info=False
    ) -> Union[str, Tuple[str, Dict[str, Any]]]:
        """
        Constructs the name of the HDF5 dataset containing digitizer
        data.

        :param board: board number
        :param channel: channel number
        :param str config_name: digitizer configuration name
        :param str adc: analog-digital-converter name
        :param bool return_info: :code:`True` will return a dictionary
            of meta-info associated with the digitizer data
            (DEFAULT :code:`False`)
        :return: digitizer dataset name. If :code:`return_info=True`,
            then returns a tuple of (dataset name, dictionary of
            meta-info)

        The returned adc information dictionary should look like::

            adc_dict = {
                'adc': str,
                'bit': int,
                'clock rate': astropy.units.Quantity,
                'configuration name': str,
                'digitizer': str,
                'nshotnum': int,
                'nt': int,
                'sample average (hardware)': int,
                'shot average (software)': int,
            }

        :raise: :exc:`NotImplementedError`
        """
        raise NotImplementedError

    @abstractmethod
    def construct_header_dataset_name(
        self, board: int, channel: int, config_name=None, adc="", **kwargs
    ) -> str:
        """
        Construct the name of the HDF5 header dataset associated with
        the digitizer dataset. The header dataset stores shot numbers
        and other shot number specific meta-data.  It also has a one-
        to-one row correspondence with the digitizer dataset.

        :param board: board number
        :param channel: channel number
        :param str config_name: digitizer configuration name
        :param str adc: analog-digital-converter name
        :returns: header dataset name associated with the digitizer
            dataset
        """
        raise NotImplementedError

    def deduce_config_active_status(self, config_name: str) -> bool:
        """
        Determines if data was recorded using the configuration
        specified by :code:`config_name`.  This is done by comparing
        the configuration name against the dataset names.

        :param config_name: digitizer configuration name
        :returns: :code:`True` if the configuration was used in
            recording the group datasets; otherwise, :code:`False`

        .. note::

            If the digitizer does not use the configuration name in the
            name of the created datasets, then the subclassing digitzier
            mapping class should override this method with a rule that
            is appropriate for the digitizer the class is being
            designed for.
        """
        active = False

        # gather dataset names
        dataset_names = []
        for name in self.group:
            if isinstance(self.group[name], h5py.Dataset):
                dataset_names.append(name)

        # if config_name is in any dataset name then config_name is
        # active
        for name in dataset_names:
            if config_name in name:
                active = True
                break

        return active

    @property
    def device_adcs(self) -> Tuple[str, ...]:
        """
        Tuple of the analog-digital-convert (adc) names integrated into
        the digitizer.
        """
        return self._device_adcs

    @property
    def device_name(self) -> str:
        """Name of digitizer"""
        return self._info["group name"]

    def get_adc_info(
        self, board: int, channel: int, adc=None, config_name=None
    ) -> Dict[str, Any]:
        """
        Get adc setup info dictionary associated with **board** and
        **channel**.

        :param board: board number
        :param channel: channel number
        :param str adc: analog-digital-converter name
        :param config_name: digitizer configuration name
        :returns: dictionary of adc setup info (bit, clock rate,
            averaging, etc.) associated with **board* and **channel**
        """
        # look for `config_name`
        if config_name is None:
            if len(self.active_configs) == 1:
                config_name = self.active_configs[0]
                warn(
                    f"`config_name` not specified, assuming '{config_name}'",
                    HDFMappingWarning,
                )
            else:
                raise ValueError("A valid `config_name` needs to be specified")
        elif self.configs[config_name]["active"] is False:
            warn(
                f"Digitizer configuration '{config_name}' is not actively used.",
                HDFMappingWarning,
            )

        # look for `adc`
        if adc is None:
            if len(self.configs[config_name]["adc"]) == 1:
                adc = self.configs[config_name]["adc"][0]
                warn(f"`adc` not specified, assuming '{adc}'", HDFMappingWarning)
            else:
                raise ValueError("A valid `adc` needs to be specified")

        # look for `board`
        adc_setup = self.configs[config_name][adc]
        found = False
        conn = (None, None, None)
        for conn in adc_setup:
            if board == conn[0]:
                found = True
                break
        if not found or not bool(board):
            raise ValueError(f"Board number ({board}) not found in setup")

        # look for `channel`
        if channel not in conn[1] or not bool(channel):
            raise ValueError(f"Channel number ({channel})  not found in setup")

        # get dictionary and add keys
        # - 'board', 'channel', 'adc', 'digitizer', and
        #   'configuration name'
        adc_info = copy.deepcopy(conn[2])
        adc_info["adc"] = adc
        adc_info["board"] = board
        adc_info["channel"] = channel
        adc_info["configuration name"] = config_name
        adc_info["digitizer"] = self.device_name

        return adc_info

    @property
    def group(self) -> h5py.Group:
        """Instance of the HDF5 digitizer group"""
        return self._digi_group

    @property
    def info(self) -> dict:
        """
        Digitizer dictionary of meta-info. For example, ::

            info = {
                'group name': 'Digitizer',
                'group path': '/foo/bar/Digitizer',
            }
        """
        return self._info
