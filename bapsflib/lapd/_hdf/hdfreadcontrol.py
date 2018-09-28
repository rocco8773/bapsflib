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
import bapsflib
import h5py
import numpy as np
import os
import time

from bapsflib._hdf_mappers.controls.templates import \
    (HDFMapControlTemplate, HDFMapControlCLTemplate)
from functools import reduce
from typing import (Any, Iterable, List, Tuple, Union)
from warnings import warn

ControlMap = Union[HDFMapControlTemplate, HDFMapControlCLTemplate]


class HDFReadControl(np.recarray):
    """
    Reads control device data from the HDF5 file.

    This class constructs and returns a structured numpy array.  The
    data in the array is grouped into two categories:

    #. shot numbers which are contained in the :code:`'shotnum'` field
    #. control device data which is represented by the remaining fields
       in the numpy array.  These field names are polymorphic and are
       defined by the control device mapping class.

    Data that is not shot number specific is stored in the :attr:`info`
    attribute.

    .. note::

        * It is assumed that control data is always extracted with the
          intent of being matched to digitizer data.
        * Only one control for each
          :class:`~bapsflib._hdf_mappers.controls.contype.ConType` can
          be specified at a time.
        * It is assumed that there is only ONE dataset associated with
          each control device configuration.
        * If multiple device configurations are saved in the same HDF5
          dataset (common in the :ibf:`'Waveform'` control device),
          then it is assumed that the configuration writing order is
          consistent for all recorded shot numbers.  That is, if
          *'config1'*, *'config2'*, and *'config3'* are recorded in that
          order for shot number 1, then that order is preserved for all
          recorded shot numbers.
    """
    __example_doc__ = """
    :Example: Here the control device :code:`'Waveform'` is used as a
        basic example:
        
        >>> # open HDF5 file
        >>> f = bapsflib.lapd.File('test.hdf5')
        >>>
        >>> # read control data
        >>> # - this is equivalent to 
        >>> #   f.read_control(['Waveform', 'config01'])
        >>> data = HDFReadControl(f, ['Waveform', 'config01'])
        >>> data.dtype
        dtype([('shotnum', '<u4'), ('command', '<U18')])
        >>>
        >>> # display shot numbers
        >>> data['shotnum']
        array([   1,    2,    3, ..., 6158, 6159, 6160], dtype=uint32)
        >>>
        >>> # show 'command' values for shot numbers 1 to 2
        >>> data['command'][0:2:]
        array(['FREQ 50000.000000', 'FREQ 50000.000000'],
              dtype='<U18')
    """
    #
    # Extracting Data:
    # - if multiple controls are specified then,
    #   ~ only one control of each contype can be in the list of
    #     controls
    #   ~ if a specified control does not exist in the HDF5 file, then
    #     a TypeError will be raised
    #   ~ if a control device configuration is not specified, then if
    #     the control has one config then that config will be assumed,
    #     otherwise, a TypeError will be raised
    #
    warn("attribute access to numpy array fields will be deprecated "
         "by Oct., access fields like data['shotnum'] NOT like "
         "data.shotnum",
         FutureWarning)

    def __new__(cls,
                hdf_file: bapsflib.lapd.File,
                controls,
                shotnum=slice(None), intersection_set=True,
                silent=False, **kwargs):
        """
        :param hdf_file: HDF5 file object
        :param controls: a list indicating the desired control device
            names and their configuration name (if more than one
            configuraiton exists)
        :type controls: Union[str, Iterable[str, Tuple[str, Any]]]
        :param shotnum: HDF5 file shot number(s) indicating data
            entries to be extracted
        :type shotnum: int, list(int), or slice(start, stop, step)
        :param bool intersection_set: :code:`True` (DEFAULT) will force
            the returned shot numbers to be the intersection of
            :data:`shotnum` and the shot numbers contained in each
            control device dataset. :code:`False` will return the union
            instead of the intersection
        :param bool silent: :code:`False` (DEFAULT).  Set :code:`True`
            to suppress command line printout of soft-warnings

        Behavior of :data:`shotnum` and :data:`intersection_set`:
            * :data:`shotnum` indexing starts at 1
            * Any :data:`shotnum` values :code:`<= 0` will be thrown out
            * If :code:`intersection_set=True`, then only data
              corresponding to shot numbers that are specified in
              :data:`shotnum` and are in all control datasets will be
              returned
            * If :code:`intersection_set=False`, then the returned array
              will have entries for all shot numbers specified in
              :data:`shotnum` but entries that correspond to control
              datasets that do not have the specified shot number will
              be given a NULL value of :code:`-99999`,
              :code:`numpy.nan`, or :code:`''`, depending on the
              :code:`numpy.dtype`.
        """
        # When inheriting from numpy, the object creation and
        # initialization is handled by __new__ instead of __init__.
        #
        # :param: controls:
        # - :data:`controls` is a list of strings or 2-element tuples
        # - if an element is a string
        #   * that string is the name of the desired control device
        #   * the control device must have only one configuration
        # - if an element is a 2-element tuple:
        #   * the 1st value is a string naming the control device
        #   * the 2nd value is the device configuration name as defined
        #     in the device mapping
        # - :data:`controls` can only contain one control device for
        #   each :data:`contype`
        # - Examples:
        #   1. a '6K Compumotor' with multiple configurations
        #
        #       controls = [('6K Compumotor', 1)]
        #
        #   2. a '6K Compumotor' with multiple configurations and a
        #      'Waveform' with one configuration
        #
        #       controls = ['Waveform, ('6K Compumotor', 1)]
        #

        # initialize timing
        tt = []
        if 'timeit' in kwargs:  # pragma: no cover
            timeit = kwargs['timeit']
            if timeit:
                tt.append(time.time())
            else:
                timeit = False
        else:
            timeit = False

        # initiate warning string
        warn_str = ''

        # ---- Condition `hdf_file`                                 ----
        # - `hdf_file` is a lapd.file object
        #
        if not isinstance(hdf_file, bapsflib.lapd.File):
            raise TypeError(
                '`hdf_file` is NOT type `bapsflib.lapd.File`')

        # grab instance of _fmap
        _fmap = hdf_file.file_map

        # Check for non-empty controls
        # if not _fmap.controls or _fmap.controls is None:
        if not bool(_fmap.controls):
            raise ValueError(
                'There are no control devices in the HDF5 file.')

        # print execution timing
        if timeit:  # pragma: no cover
            tt.append(time.time())
            print('tt - hdf_file conditioning: '
                  '{} ms'.format((tt[-1] - tt[-2]) * 1.E3))

        # ---- Condition 'controls' Argument                        ----
        # - some calling routines (such as, lapd.File.read_data)
        #   already properly condition 'controls', so passing a keyword
        #   'assume_controls_conditioned' allows for a bypass of
        #   conditioning here
        #
        try:
            if not kwargs['assume_controls_conditioned']:
                controls = condition_controls(hdf_file, controls)
        except KeyError:
            controls = condition_controls(hdf_file, controls)

        # print execution timing
        if timeit:  # pragma: no cover
            tt.append(time.time())
            print('tt - condition controls: '
                  '{} ms'.format((tt[-1] - tt[-2]) * 1.E3))

        # ---- Condition shotnum                                    ----
        # shotnum -- global HDF5 file shot number
        #            ~ this is the parameter used to link values between
        #              datasets
        #
        # Through conditioning the following are (re-)defined:
        # index   -- row index of the control dataset(s)
        #            ~ numpy.ndarray
        #            ~ dtype = np.integer
        #            ~ shape = (len(controls), num_of_indices)
        #
        # shotnum -- global HDF5 shot number
        #            ~ index at 1
        #            ~ will be a filtered version of input kwarg shotnum
        #              based on intersection_set
        #            ~ numpy.ndarray
        #            ~ dtype = np.uint32
        #            ~ shape = (sn_size, )
        #
        # sni     -- bool array for providing a one-to-one mapping
        #            between shotnum and index
        #            ~ shotnum[sni] = cdset[index, shotnumkey]
        #            ~ numpy.ndarray
        #            ~ dtype = np.bool
        #            ~ shape = (len(controls), sn_size)
        #            ~ np.count_nonzer(arr[0,...]) = num_of_indices
        #
        # - Indexing behavior: (depends on intersection_set)
        #
        #   ~ shotnum
        #     * intersection_set = True
        #       > the returned array will only contain shot numbers that
        #         are in the intersection of shotnum and all the
        #         specified control device datasets
        #
        #     * intersection_set = False
        #       > the returned array will contain all shot numbers
        #         specified by shotnum (>= 1)
        #       > if a dataset does not included a shot number contained
        #         in shotnum, then its entry in the returned array will
        #         be given a NULL value depending on the dtype
        #
        # Gather control datasets and associated shot number field names
        cdset_dict = {}
        shotnumkey_dict = {}
        for control in controls:
            # control name (cname) and configuration name (cconfn)
            cname = control[0]
            cconfn = control[1]

            # gather control datasets and shotnumkey's
            cmap = _fmap.controls[cname]
            cdset_path = cmap.configs[cconfn]['dset paths'][0]
            cdset_dict[cname] = hdf_file.get(cdset_path)
            try:
                shotnumkey = \
                    cmap.configs[cconfn]['shotnum']['dset field'][0]
                shotnumkey_dict[cname] = shotnumkey
            except KeyError:
                raise ValueError(
                    'no shot number field defined for control device')

        # Catch shotnum if a slice object or int
        # - For either case, convert shotnum to a list
        #
        shotnum = condition_shotnum(shotnum,
                                    cdset_dict,
                                    shotnumkey_dict)

        # Ensure 'shotnum' is valid
        # - at this point 'shotnum' should be a list
        # - after this block (by the time you get to
        #   ---- Build obj ----) 'shotnum' will be converted to a numpy
        #   1D array containing the shot numbers to be included in the
        #   returned obj array
        #
        # Notes:
        # 1. shotnum can not be converted to a np.array until after
        #    shotnum, index, and sni are determined for each control
        # 2. all entries in shotnum_dict, index_dict, and sni_dict
        #    should be np.arrays
        # 3. shotnum values used to fill shotnum_dict should not go
        #    through an intersection filtering in here, this will be
        #    done after this for-loop
        #
        index_dict = {}
        shotnum_dict = {}
        sni_dict = {}
        for control in controls:
            # control name (cname) and configuration name (cconfn)
            cname = control[0]
            cconfn = control[1]
            cmap = _fmap.controls[cname]

            # get a conditioned version of index, shotnum, and sni for
            # each control
            index_dict[cname], shotnum_dict[cname], sni_dict[cname] = \
                build_shotnum_dset_relation(shotnum, cdset_dict[cname],
                                            shotnumkey_dict[cname],
                                            cmap, cconfn)

        # re-filter index, shotnum, sni
        if intersection_set:
            shotnum, shotnum_dict, sni_dict, index_dict = \
                do_shotnum_intersection(shotnum,
                                        shotnum_dict,
                                        sni_dict,
                                        index_dict)

        # print execution timing
        if timeit:  # pragma: no cover
            tt.append(time.time())
            print('tt - condition shotnum: '
                  '{} ms'.format((tt[-1] - tt[-2]) * 1.E3))

        # ---- Build obj ----
        # Define dtype and shape for numpy array
        shape = shotnum.shape
        dtype = [('shotnum', '<u4', 1)]
        for control in controls:
            # control name (cname) and configuration name (cconfn)
            cname = control[0]
            cconfn = control[1]

            # add fields
            cconfig = _fmap.controls[cname].configs[cconfn]
            for field_name, fconfig in \
                    cconfig['state values'].items():
                dtype.append((
                    field_name,
                    fconfig['dtype'],
                    fconfig['shape']
                ))

        # print execution timing
        if timeit:  # pragma: no cover
            tt.append(time.time())
            print('tt - define dtype: '
                  '{} ms'.format((tt[-1] - tt[-2]) * 1.E3))

        # Initialize Control Data
        data = np.empty(shape, dtype=dtype)
        data['shotnum'] = shotnum.view()

        # print execution timing
        if timeit:  # pragma: no cover
            tt.append(time.time())
            print('tt - initialize data np.ndarray: '
                  '{} ms'.format((tt[-1] - tt[-2]) * 1.E3))

        # Assign Control Data to Numpy array
        for control in controls:
            # control name (cname) and configuraiton name (cconfn)
            cname = control[0]
            cconfn = control[1]

            # get control dataset
            cmap = _fmap.controls[cname]
            cconfig = cmap.configs[cconfn]
            cdset = cdset_dict[cname]
            sni = sni_dict[cname]
            index = index_dict[cname]
            if isinstance(index, np.ndarray):
                index = index.tolist()

            # populate control data array
            # 1. scan over numpy fields
            # 2. scan over the dset fields that will fill the numpy
            #    fields
            # 3. split between a command list fill or a direct fill
            # 4. NaN fill if intersection_set = False
            #
            for nf_name, fconfig \
                    in cconfig['state values'].items():
                # nf_name
                #   the numpy field name
                # fconfig
                #   the mapping dictionary for nf_name
                for npi, df_name in enumerate(fconfig['dset field']):
                    # df_name
                    #   the dset field name that will fill the numpy
                    #   field
                    # npi
                    #   the index of the numpy array corresponding to
                    #   nf_name that df_name will fill
                    #
                    # assign data
                    if cmap.has_command_list:
                        # command list fill
                        # get command list
                        cl = fconfig['command list']

                        # retrieve the array of command indices
                        ci_arr = cdset[index, df_name]

                        # assign command values to data
                        for ci, command in enumerate(cl):
                            # Order of operations
                            # 1. find where command index (ci) is in the
                            #    command index array (ci_arr)
                            # 2. construct a new sni for ci
                            # 3. fill data
                            #
                            # find where ci is in ci_arr
                            ii = np.where(ci_arr == ci, True, False)

                            # construct new sni
                            sni_for_ci = np.zeros(sni.shape, dtype=bool)
                            sni_for_ci[np.where(sni)[0][ii]] = True

                            # assign values
                            data[nf_name][sni_for_ci] = command
                    else:
                        # direct fill (NO command list)
                        if data.dtype[nf_name].shape != ():
                            # field contains an array (e.g. 'xyz')
                            data[nf_name][sni, npi] = \
                                cdset[index, df_name].view()
                        else:
                            # field is a constant
                            data[nf_name][sni] = \
                                cdset[index, df_name].view()

                    # handle NaN fill
                    if not intersection_set:
                        # overhead
                        sni_not = np.logical_not(sni)
                        dtype = data.dtype[nf_name].base

                        #
                        if data.dtype[nf_name].shape != ():
                            ii = np.s_[sni_not, npi]
                        else:
                            ii = np.s_[sni_not]

                        # NaN fill
                        if np.issubdtype(dtype, np.integer):
                            # any integer, signed or not
                            data[nf_name][ii] = -99999
                        elif np.issubdtype(dtype, np.floating):
                            # any float type
                            data[nf_name][ii] = np.nan
                        elif np.issubdtype(dtype, np.flexible):
                            # string, unicode, void
                            data[nf_name][ii] = ''
                        else:
                            # no real NaN concept exists
                            # - this shouldn't happen though
                            warn('dtype ({}) of '.format(dtype)
                                 + '{} has no Nan '.format(nf_name)
                                 + 'concept...no NaN fill done')

            # print execution timing
            if timeit:  # pragma: no cover
                tt.append(time.time())
                print('tt - fill data - '
                      + '{}: '.format(cname)
                      + '{} ms'.format((tt[-1] - tt[-2]) * 1.E3))

        # print execution timing
        if timeit:  # pragma: no cover
            n_controls = len(controls)
            tt.append(time.time())
            print('tt - fill data array: '
                  '{} ms'.format((tt[-1] - tt[-n_controls-2]) * 1.E3)
                  + ' (intersection_set={})'.format(intersection_set))

        # Construct obj
        obj = data.view(cls)

        # assign dataset info
        # TODO: add a dict key for each control w/ controls config
        # - control configs dict should include:
        #   ~ 'contype'
        #   ~ 'dataset name'
        #   ~ 'dataset path'
        #
        obj._info = {
            'source file': os.path.abspath(hdf_file.filename),
            'controls': controls,
            'probe name': None,
            'port': (None, None),
        }

        # populate meta-info from controls.configs
        # TODO: populate info from controls.configs
        #

        # print warnings
        if not silent and warn_str != '':
            print(warn_str)

        # print execution timing
        if timeit:  # pragma: no cover
            tt.append(time.time())
            print('tt - total execution time: '
                  '{} ms'.format((tt[-1] - tt[0]) * 1.E3))

        # return obj
        return obj

    def __array_finalize__(self, obj):
        # according to numpy documentation:
        #  __array__finalize__(self, obj) is called whenever the system
        #  internally allocates a new array from obj, where obj is a
        #  subclass (subtype) of the (big)ndarray. It can be used to
        #  change attributes of self after construction (so as to ensure
        #  a 2-d matrix for example), or to update meta-information from
        #  the parent. Subclasses inherit a default implementation of
        #  this method that does nothing.
        if obj is None:
            return

        # Define info attribute
        # - getattr() searches obj for the 'info' attribute. If the
        #   attribute exists, then it's returned. If the attribute does
        #   NOT exist, then the 3rd arg is returned as a default value.
        self._info = getattr(obj, '_info', {
            'source file': None,
            'controls': None,
            'probe name': None,
            'port': (None, None),
        })

    @property
    def info(self) -> dict:
        """A dictionary of meta-info for the control device."""
        return self._info


# add example to __new__ docstring
HDFReadControl.__new__.__doc__ += "\n"
for line in HDFReadControl.__example_doc__.splitlines():
    HDFReadControl.__new__.__doc__ += "    " + line + "\n"


def condition_controls(hdf_file: bapsflib.lapd.File,
                       controls: Any) -> List[Tuple[str, Any]]:
    """
    Conditions the **controls** argument for :class:`HDFReadControl`.

    :param hdf_file: HDF5 object instance
    :param controls: `controls` argument to be conditioned
    :return: list containing tuple pairs of control device name and
        desired configuration name

    :Example:

        >>> from bapsflib import lapd
        >>> f = lapd.File('sample.hdf5')
        >>> controls = ['Wavefrom', ('6K Compumotor', 3)]
        >>> conditioned_controls = condition_controls(f, controls)
        >>> conditioned_controls
        [('Waveform', 'config01'), ('6K Compumotor', 3)]

    """
    # grab instance of file mapping
    _fmap = hdf_file.file_map

    # -- condition 'controls' argument                              ----
    # - controls is:
    #   1. a string or Iterable
    #   2. each element is either a string or tuple
    #   3. if tuple, then length <= 2
    #      ('control name',) or ('control_name', config_name)
    #
    # check if NULL
    if not bool(controls):
        # catch a null controls
        raise ValueError('controls argument is NULL')

    # make string a list
    if isinstance(controls, str):
        controls = [controls]

    # condition Iterable
    if isinstance(controls, Iterable):
        # all list items have to be strings or tuples
        if not all(isinstance(con, (str, tuple)) for con in controls):
            raise TypeError('all elements of `controls` must be of '
                            'type string or tuple')

        # condition controls
        new_controls = []
        for control in controls:
            if isinstance(control, str):
                name = control
                config_name = None
            else:
                # tuple case
                if len(control) > 2:
                    raise ValueError(
                        "a `controls` tuple element must be specified "
                        "as ('control name') or, "
                        "('control name', config_name)")

                name = control[0]
                config_name = None if len(control) == 1 else control[1]

            # ensure proper control and configuration name are defined
            if name in [cc[0] for cc in new_controls]:
                raise ValueError(
                    'Control device ({})'.format(control)
                    + ' can only have one occurrence in controls')
            elif name in _fmap.controls:
                if config_name in _fmap.controls[name].configs:
                    # all is good
                    pass
                elif len(_fmap.controls[name].configs) == 1 \
                        and config_name is None:
                    config_name = list(_fmap.controls[name].configs)[0]
                else:
                    raise ValueError(
                        "'{}' is not a valid ".format(config_name)
                        + "configuration name for control device "
                        + "'{}'".format(name))
            else:
                raise ValueError('Control device ({})'.format(name)
                                 + ' not in HDF5 file')

            # add control to new_controls
            new_controls.append((name, config_name))
    else:
        raise TypeError('`controls` argument is not Iterable')

    # enforce one control per contype
    checked = []
    controls = new_controls
    for control in controls:
        # control is a tuple, not a string
        contype = _fmap.controls[control[0]].contype

        if contype in checked:
            raise TypeError('`controls` has multiple devices per '
                            'contype')
        else:
            checked.append(contype)

    # return conditioned list
    return controls


def condition_shotnum(shotnum: Any,
                      dset_dict: dict,
                      shotnumkey_dict: dict) -> np.ndarray:
    """
    Conditions the **shotnum** argument for
    :class:`~bapsflib.lapd._hdf.hdfreadcontrol.HDFReadControl`.

    :param shotnum: desired HDF5 shot numbers
    :param dset_dict: dictionary of all control dataset instances
    :param shotnumkey_dict: dictionary of the shot number field name
        for each control dataset in dset_dict
    :return: conditioned **shotnum** numpy array
    """
    # Acceptable `shotnum` types
    # 1. int
    # 2. slice() object
    # 3. List[int, ...]
    # 4. np.array (dtype = np.integer and ndim = 1)
    #
    # Catch each `shotnum` type and convert to numpy array
    #
    if isinstance(shotnum, int):
        if shotnum <= 0 or isinstance(shotnum, bool):
            raise ValueError(
                "Valid `shotnum` ({})".format(shotnum)
                + " not passed. Resulting array would be NULL.")

        # convert
        shotnum = np.array([shotnum], dtype=np.uint32)

    elif isinstance(shotnum, list):
        # ensure all elements are int
        if not all(isinstance(sn, int) for sn in shotnum):
            raise ValueError('Valid `shotnum` not passed. All values '
                             'NOT int.')

        # remove shot numbers <= 0
        shotnum.sort()
        shotnum = list(set(shotnum))
        shotnum.sort()
        if min(shotnum) <= 0:
            # remove values less-than or equal to 0
            new_sn = [sn for sn in shotnum if sn > 0]
            shotnum = new_sn

        # ensure not NULL
        if len(shotnum) == 0:
            raise ValueError('Valid `shotnum` not passed. Resulting '
                             'array would be NULL')

        # convert
        shotnum = np.array(shotnum, dtype=np.uint32)

    elif isinstance(shotnum, slice):
        # determine largest possible shot number
        last_sn = [
            dset_dict[cname][-1, shotnumkey_dict[cname]] + 1
            for cname in dset_dict
        ]
        if shotnum.stop is not None:
            last_sn.append(shotnum.stop)
        stop_sn = max(last_sn)

        # get the start, stop, and step for the shot number array
        start, stop, step = shotnum.indices(stop_sn)

        # re-define `shotnum`
        shotnum = np.arange(start, stop, step, dtype=np.int32)

        # remove shot numbers <= 0
        shotnum = np.delete(shotnum, np.where(shotnum <= 0)[0])
        shotnum = shotnum.astype(np.uint32)

        # ensure not NULL
        if shotnum.size == 0:
            raise ValueError('Valid `shotnum` not passed. Resulting '
                             'array would be NULL')

    elif isinstance(shotnum, np.ndarray):
        shotnum = shotnum.squeeze()
        if shotnum.ndim != 1 \
                or not np.issubdtype(shotnum.dtype, np.integer) \
                or bool(shotnum.dtype.names):
            raise ValueError('Valid `shotnum` not passed')

        # remove shot numbers <= 0
        shotnum.sort()
        shotnum = np.delete(shotnum, np.where(shotnum <= 0)[0])
        shotnum = shotnum.astype(np.uint32)

        # ensure not NULL
        if shotnum.size == 0:
            raise ValueError('Valid `shotnum` not passed. Resulting '
                             'array would be NULL')
    else:
        raise ValueError('Valid `shotnum` not passed')

    # return
    return shotnum


def build_shotnum_dset_relation(
        shotnum: np.ndarray,
        dset: h5py.Dataset,
        shotnumkey: str,
        cmap: ControlMap,
        cconfn: Any) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compares the **shotnum** numpy array to the specified dataset,
    **dset**, to determine which indices contain the desired shot
    number(s).  As a results, three numpy arrays are returned which
    satisfy the rule::

        shotnum[sni] = dset[index, shotnumkey]

    where **shotnum** is the original shot number array, **sni** is a
    boolean numpy array masking which shot numbers were determined to
    be in the dataset, and **index** is an array of indices
    corresponding to the desired shot number(s).

    :param shotnum: desired HDF5 shot number(s)
    :param dset: control device dataset
    :type dset: :class:`h5py.Dataset`
    :param str shotnumkey: field name in the control device dataset that
        contains shot numbers
    :param cmap: mapping object for control device
    :param str cconfn: configuration name for the control device
    :return: :code:`index`, :code:`shotnum`, and :code:`sni` numpy
        arrays

    .. note::

        This function leverages the functions
        :func:`~bapsflib.lapd._hdf.hdfreadcontrol.condition_shotnum_list_simple`
        and
        :func:`~bapsflib.lapd._hdf.hdfreadcontrol.condition_shotnum_list_complex`
    """
    # Inputs:
    # shotnum      - the desired shot number(s)
    # dset         - the control device dataset
    # shotnumkey   - field name for the shot number column in dset
    # cmap         - file mapping object for the control device
    # cconfn       - configuration for control device
    #
    # Returns:
    # index     np.array(dtype=uint32)  - dset row index for the
    #                                     specified shotnum
    # shotnum   np.array(dtype=uint32)  - shot numbers
    # sni       np.array(dtype=bool)    - shotnum mask such that:
    #
    #            shotnum[sni] = dset[index, shotnumkey]
    #
    # Initialize some vars
    n_configs = len(cmap.configs)
    configs_per_row = 1 if cmap.one_config_per_dset else n_configs

    # Calc. index, shotnum, and sni
    if configs_per_row == 1:
        # the dataset only saves data for one configuration
        index, shotnum, sni = \
            build_sndr_for_simple_dset(shotnum, dset, shotnumkey)
    else:
        # the dataset saves data for multiple configurations
        index, shotnum, sni = \
            condition_shotnum_list_complex(shotnum, dset, shotnumkey,
                                           cmap, cconfn)

    # return calculated arrays
    return index.view(), shotnum.view(), sni.view()


def build_sndr_for_simple_dset(
        shotnum: np.ndarray,
        dset: h5py.Dataset,
        shotnumkey: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compares the **shotnum** numpy aray to the specified "simple"
    dataset, **dset**, to determine which indices contain the desired
    shot number(s).  As a results, three numpy arrays are returned which
    satisfy the rule::

        shotnum[sni] = dset[index, shotnumkey]

    where **shotnum** is the original shot number array, **sni** is a
    boolean numpy array masking which shot numbers were determined to
    be in the dataset, and **index** is an array of indices
    corresponding to the desired shot number(s).

    A "simple" dataset is a dataset in which the data for only ONE
    configuration is recorded.

    :param shotnum: desired HDF5 shot number
    :param dset: control device dataset
    :type dset: :class:`h5py.Dataset`
    :param str shotnumkey: field name in the control device dataset that
        contains the shot numbers
    :return: :code:`index`, :code:`shotnum`, and :code:`sni` numpy
        arrays
    """
    # this is for a dataset that only records data for one configuration
    #
    # get corresponding indices for shotnum
    # build associated sni array
    #
    if dset.shape[0] == 1:
        # only one possible shot number
        only_sn = dset[0, shotnumkey]
        sni = np.where(shotnum == only_sn, True, False)
        index = np.array([0]) \
            if True in sni else np.empty(shape=0, dtype=np.uint32)
    else:
        # get 1st and last shot number
        first_sn, last_sn = dset[[-1, 0], shotnumkey]

        if last_sn - first_sn + 1 == dset.shape[0]:
            # shot numbers are sequential
            index = shotnum - first_sn

            # build sni and filter index
            sni = np.where(index < dset.shape[0], True, False)
            index = index[sni]
        else:
            # shot numbers are NOT sequential
            step_front_read = shotnum[-1] - first_sn
            step_end_read = last_sn - shotnum[0]

            if dset.shape[0] <= 1 + min(step_front_read,
                                        step_end_read):
                # dset.shape is smaller than the theoretical reads from
                # either end of the array
                #
                dset_sn = dset[shotnumkey].view()
                sni = np.isin(shotnum, dset_sn)

                # define index
                index = np.where(np.isin(dset_sn, shotnum))[0]
            elif step_front_read <= step_end_read:
                # extracting from the beginning of the array is the
                # smallest
                some_dset_sn = dset[0:step_front_read + 1, shotnumkey]
                sni = np.isin(shotnum, some_dset_sn)

                # define index
                index = np.where(np.isin(some_dset_sn, shotnum))[0]
            else:
                # extracting from the end of the array is the smallest
                start, stop, step = slice(-step_end_read - 1,
                                          None,
                                          None).indices(dset.shape[0])
                some_dset_sn = dset[start::, shotnumkey]
                sni = np.isin(shotnum, some_dset_sn)

                # define index
                # NOTE: if index is empty (i.e. index.shape[0] == 0)
                #       then adding an int still returns an empty array
                index = np.where(np.isin(some_dset_sn, shotnum))[0]
                index += start

    # return calculated arrays
    return index.view(), shotnum.view(), sni.view()


# rename to condition_shotnum_w_complex_dset
def condition_shotnum_list_complex(shotnum, cdset, shotnumkey, cmap,
                                   cconfn):
    """
    Conditions **shotnum** (when a `list`) against control dataset
    **cdset** when the control dataset contains recorded data for
    multiple device configurations.

    .. admonition:: Dataset Assumption

        There is an assumption that each shot number spans **n_configs**
        number of rows in the dataset, where **n_configs** is the number
        of control device configurations.  It is also assumed that the
        order in which the configs are recorded is the same for each
        shot number.  That is, if there are 3 configs (config01,
        config02, and config03) and the first three rows of the dataset
        are recorded in that order, then each following grouping of
        three rows will maintain that order.

    :param shotnum: desired HDF5 shot number
    :type shotnum: :class:`numpy.ndarray`
    :param cdset: control device dataset
    :type cdset: :class:`h5py.Dataset`
    :param str shotnumkey: field name in the control device dataset that
        contains the shot numbers
    :param cmap: mapping object for control device
    :param cconfn: configuration name for the control device
    :return: index, shotnum, sni

    .. note::

        The returned :class:`numpy.ndarray`'s (:const:`index`,
        :const:`shotnum`, and :const:`sni`) follow the rule::

            shotnum[sni] = cdset[index, shotnumkey]
    """
    # this is for a dataset that only records data for one configuration
    #
    # Ensure there is only one dataset for all configs
    # Note: we should only get to this point if n_dsets != n_configs
    n_dsets = len(cmap.dataset_names)
    n_configs = len(cmap.configs)
    if n_dsets != 1:
        raise ValueError(
            'Control has {} datasets and'.format(n_dsets)
            + ' {} configurations, do NOT'.format(n_configs)
            + ' know how to handle')

    # determine configkey
    # - configkey is the dataset field name for the column that contains
    #   the associated configuration name
    #
    configkey = ''
    for df in cdset.dtype.names:
        if 'configuration' in df.casefold():
            configkey = df
            break
    if configkey == '':
        raise ValueError(
            'Can NOT find configuration field in the control'
            + ' ({}) dataset'.format(cmap.device_name))

    # find index
    if cdset.shape[0] == n_configs:
        # only one possible shotnum, index can be 0 to n_configs-1
        #
        # NOTE: The HDF5 configuration field stores a string with the
        #       name of the configuration.  When reading that into a
        #       numpy array the string becomes a byte string (i.e. b'').
        #       When comparing with np.where() the comparing string
        #       needs to be encoded (i.e. cconfn.encode()).
        #
        only_sn = cdset[0, shotnumkey]
        sni = np.where(shotnum == only_sn, True, False)

        # construct index
        if True not in sni:
            # shotnum does not contain only_sn
            index = np.empty(shape=0, dtype=np.uint32)
        else:
            config_name_arr = cdset[0:n_configs, configkey]
            index = np.where(config_name_arr == cconfn.encode())[0]

            if index.size != 1:
                # something went wrong...no configurations are found
                # and, thus, the routines assumption's do not match
                # the format of the dataset
                raise ValueError
    else:
        # get 1st and last shot number
        first_sn, last_sn = cdset[[-1, 0], shotnumkey]

        # find sub-group index corresponding to the requested device
        # configuration
        config_name_arr = cdset[0:n_configs, configkey]
        config_where = np.where(config_name_arr == cconfn.encode())[0]
        if config_where.size == 1:
            config_subindex = config_where[0]
        else:
            # something went wrong...either no configurations
            # are found or the routine's assumptions do not
            # match the format of the dataset
            raise ValueError

        # construct index for remaining scenarios
        if n_configs * (last_sn - first_sn + 1) == cdset.shape[0]:
            # shot numbers are sequential and there are n_configs per
            # shot number
            index = shotnum - first_sn

            # adjust index to correspond to associated configuration
            # - stretch by n_configs then shift by config_subindex
            #
            index = (n_configs * index) + config_subindex

            # build sni and filter index
            sni = np.where(index < cdset.shape[0], True, False)
            index = index[sni]
        else:
            # shot numbers are NOT sequential
            step_front_read = shotnum[-1] - first_sn
            step_end_read = last_sn - shotnum[0]

            # construct index and sni
            if cdset.shape[0] <= n_configs * (
                    min(step_front_read, step_end_read) + 1):
                # cdset.shape is smaller than the theoretical
                # sequential array
                cdset_sn = cdset[config_subindex::n_configs,
                                 shotnumkey].view()
                sni = np.isin(shotnum, cdset_sn)
                index = np.where(np.isin(cdset_sn, shotnum))[0]

                # adjust index to correspond to associated configuration
                index = (config_subindex + 1) * index
            elif step_front_read <= step_end_read:
                # extracting from the beginning of the array is the
                # smallest
                start = config_subindex
                stop = n_configs * (step_front_read + 1)
                stop += config_subindex
                step = n_configs
                some_cdset_sn = cdset[start:stop:step,
                                      shotnumkey].view()
                sni = np.isin(shotnum, some_cdset_sn)
                index = np.where(np.isin(some_cdset_sn, shotnum))[0]

                # adjust index to correspond to associated configuration
                index = (config_subindex + 1) * index
            else:
                # extracting from the end of the array is the
                # smallest
                start, stop, step = \
                    slice(-n_configs * (step_end_read + 1),
                          None,
                          n_configs).indices(cdset.shape[0])
                start += config_subindex
                some_cdset_sn = cdset[start:stop:step,
                                      shotnumkey].view()
                sni = np.isin(shotnum, some_cdset_sn)
                index = np.where(np.isin(some_cdset_sn, shotnum))

                # adjust index to correspond to associated configuration
                index = (config_subindex + 1) * index
                index += start

    # return calculated arrays
    return index.view(), shotnum.view(), sni.view()


def do_shotnum_intersection(shotnum, shotnum_dict, sni_dict, index_dict):
    # determine intersecting shot numbers
    # - I'm assuming no intersection as been performed yet
    #
    sn_list = [shotnum_dict[key][sni_dict[key]]
               for key in shotnum_dict]
    sn_list.append(shotnum)
    shotnum_intersect = reduce(
        lambda x, y: np.intersect1d(x, y, assume_unique=True),
        sn_list)
    if shotnum_intersect.shape[0] == 0:
        raise ValueError(
            'Input shotnum would result in a null array')
    else:
        shotnum = shotnum_intersect

    # now filter
    for cname in shotnum_dict:
        new_sn_mask = np.isin(
            shotnum_dict[cname][sni_dict[cname]], shotnum)
        new_sn = \
            shotnum_dict[cname][sni_dict[cname]][new_sn_mask]
        new_index = index_dict[cname][new_sn_mask]
        shotnum_dict[cname] = new_sn
        index_dict[cname] = new_index
        sni_dict[cname] = np.ones(new_index.shape[0],
                                  dtype=bool)

    return shotnum, shotnum_dict, sni_dict, index_dict
