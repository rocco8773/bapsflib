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
#
import copy
import numpy as np

from warnings import  warn


class hdfReadMSI(np.recarray):
    """
    Reads MSI diagnostic data from the HDF5 file.
    """
    def __new__(cls, hdf_file, msi_diag, **kwargs):
        # ---- Condition `hdf_file` ----
        # grab file_map
        # - also ensurse hdf_file is a lapdhdf.file object
        #
        try:
            file_map = hdf_file.file_map
        except AttributeError:
            raise AttributeError(
                'hdf_file needs to be of type lapdhdf.File')

        # ---- Condition `msi_diag` ----
        # ensure msi_diag is a string
        if not isinstance(msi_diag, str):
            raise TypeError('arg `msi_diag` needs to be a str')

        # allow for alias names of MSI diagnostics
        if msi_diag in ['interferometer',
                        'Interferometer',
                        'interferometer array']:
            msi_diag = 'Interferometer array'

        # get diagnostic map
        try:
            diag_map = hdf_file.file_map.msi[msi_diag]
        except KeyError:
            raise ValueError(
                'Specified MSI Diagnostic is not among known'
                'diagnostics')

        # ---- Construct shape and dtype for np.array ----
        shape = diag_map.configs['shape']
        dtype_list = []

        # add 'shotnum' field
        dtype_list.append(('shotnum',
                           diag_map.configs['shotnum']['dtype']))

        # add signal fields
        sig_shape = None
        for field in diag_map.configs['signals']:
            shape_list = diag_map.configs['signals'][field]['shape']
            if len(shape_list) != 1:
                # need to ensure all datasets have the same dimensions
                # - currently no handling datasets with differing dims
                if shape_list.count(shape_list[0]) != len(shape_list):
                    raise ValueError(
                        "Can not handle grouping of datasets with "
                        "differing shapes")

            # ensure all signal fields have the same number of rows
            # - if ndims = 1, then assuming one row
            if sig_shape is None:
                sig_shape = shape_list[0]
            else:
                if len(sig_shape) != len(shape_list[0]):
                    raise ValueError(
                        "all signal fields must have the same number"
                        "of rows")
                elif len(sig_shape) != 1:
                    if sig_shape[0] != shape_list[0][0]:
                        raise ValueError(
                            "all signal fields must have the same "
                            "number of rows")

            # add
            dtype_list.append((
                field,
                diag_map.configs['signals'][field]['dtype'],
                shape_list[0]
            ))

        # add 'meta' fields
        # - all 'meta' fields needs to have the same number of rows as
        #   the signal fields
        # TODO: NEED TO ADD MORE CONDITIONING OF CONSISTENT SHAPE VALUES
        meta_shape = diag_map.configs['meta']['shape']
        meta_dtype_list = []
        for field in diag_map.configs['meta']:
            # skip the 'shape' field
            if field == 'shape':
                continue

            # ensure every entry has the same shape
            shape_list = diag_map.configs['meta'][field]['shape']
            if len(shape_list) != 1:
                # need to ensure all datasets have the same dimensions
                # - currently no handling datasets with differing dims
                if shape_list.count(shape_list[0]) != len(shape_list):
                    raise ValueError(
                        "Can not handle grouping of datasets with "
                        "differing shapes")

            # add to meta_dtype_list
            meta_dtype_list.append((
                field,
                diag_map.configs['meta'][field]['dtype'],
                shape_list[0]
            ))

        # add 'meta' to dtype_list
        dtype_list.append((
            'meta',
            meta_dtype_list,
            meta_shape
        ))

        # define dtype
        dtype = np.dtype(dtype_list)

        # ---- Define and Populate Numpy Array ----
        data = np.empty(shape, dtype=dtype)

        # fill 'shotnum'
        # TODO: ADD CASE FOR 'DSET FIELD' IS NONE
        sn_config = diag_map.configs['shotnum']
        for ii, path in enumerate(sn_config['dset paths']):
            # get dataset
            dset = hdf_file[path]

            # fill array
            if ii == 0:
                data['shotnum'] = dset[:, sn_config['dset field']]
            else:
                if not np.array_equal(data['shotnum'],
                                      dset[sn_config['dset field']]):
                    raise ValueError(
                        'Datasets do NOT have the same shot number '
                        'values, do NOT know how to handle')

        # fill 'signals'
        # TODO: ADD CASE FOR 'DSET FIELD' IS NOT NONE
        sig_config = diag_map.configs['signals']
        for field in sig_config:
            for ii, path in enumerate(sig_config[field]['dset paths']):
                # get dataset
                dset = hdf_file[path]

                # fill array
                data[field][:, ii, ...] = dset

        # fill 'meta'
        # TODO: ADD CASE FOR 'DSET FIELD' IS NONE
        meta_config = diag_map.configs['meta']
        for field in meta_config:
            # skip 'shape' key
            if field == 'shape':
                continue

            # scan thru all datsets
            for ii, path in enumerate(meta_config[field]['dset paths']):
                # get dataset
                dset = hdf_file[path]

                # fill array
                data['meta'][field][:, ii, ...] = \
                    dset[meta_config[field]['dset field']]

        # ---- Define `obj` ----
        obj = data.view(cls)

        # ---- Define `info` attribute ----
        obj._info = {
            'hdf file': hdf_file.filename.split('/')[-1],
            'diagnostic name': diag_map.diagnostic_name,
            'diagnostic path': diag_map.info['group path']
        }
        for key, val in diag_map.configs.items():
            if key not in ['shape', 'shotnum', 'signals', 'meta']:
                obj._info[key] = copy.deepcopy(val)

        # ---- Return `obj` ----
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

        # Define _info attribute
        self._info = getattr(obj, '_info', {
            'hdf file': None,
            'diagnostic name': None,
            'diagnostic path': None
        })

    @property
    def info(self):
        return self._info.copy()


