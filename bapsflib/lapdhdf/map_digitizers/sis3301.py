# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017 Erik T. Everson and contributors
#
# License:
#
# TODO: consider having hdfMap_digi_sis3301 become digi_group
#  i.e. def __init__(self, digi_group):
#           digi_group.__init__()
#
import h5py


class hdfMap_digi_sis3301(object):
    __predefined_adc = ['SIS 3301']

    def __init__(self, digi_group):
        # condition digi_group arg
        if isinstance(digi_group, h5py.Group):
            self.__digi_group = digi_group
        else:
            raise TypeError('digi_group is not of type h5py.Group')

        self.info = {'group name': digi_group.name.split('/')[-1],
                     'group path': digi_group.name}

        self.data_configs = {}
        self.__build_data_configs()

    @property
    def digi_group(self):
        return self.__digi_group

    def __build_data_configs(self):
        """
        Builds self.data_configs dictionary. A dict. entry follows:

        data_configs[config_name] = {
            'active': True/False,
            'crates: [list of active SIS crates],
            'group name': 'name of config group',
            'group path': 'absolute path to config group',
            'SIS 3301': [(brd,
                [ch,],
                {'bit': 14,
                'sample rate': (100.0, 'MHz')}
                ), ]
            }

        :return:
        """
        # collect digi_group's dataset names and sub-group names
        subgroup_names = []
        dataset_names = []
        for key in self.digi_group.keys():
            if isinstance(self.digi_group[key], h5py.Dataset):
                dataset_names.append(key)
            if isinstance(self.digi_group[key], h5py.Group):
                subgroup_names.append(key)

        # populate self.data_configs
        for name in subgroup_names:
            is_config, config_name = self.parse_config_name(name)
            if is_config:
                # initialize configuration name in the config dict
                self.data_configs[config_name] = {}

                # determine if config is active
                self.data_configs[config_name]['active'] = \
                    self.is_config_active(config_name, dataset_names)

                # assign active adc's to the configuration
                self.data_configs[config_name]['adc'] = ['SIS 3301']

                # add 'group name'
                self.data_configs[config_name]['group name'] = name

                # add 'group path'
                self.data_configs[config_name]['group path'] = \
                    self.digi_group[name].name

                # add adc info
                self.data_configs[config_name]['SIS 3301'] = \
                    self.__adc_info('SIS 3301', self.digi_group[name])

    @staticmethod
    def parse_config_name(name):
        """
        Parses 'name' to see if it matches the naming scheme for a
        data configuration group.  A group representing a data
        configuration has the scheme:

            Configuration: config_name

        :param name:
        :return:
        """
        split_name = name.split()
        is_config = True if split_name[0] == 'Configuration:' else False
        config_name = ' '.join(split_name[1::]) if is_config else None
        return is_config, config_name

    @staticmethod
    def is_config_active(config_name, dataset_names):
        """
        The naming of a dataset starts with the name of its
        corresponding configuration.  This scans 'dataset_names'
        fo see if 'config_name' is used in the list of datasets.

        :param config_name:
        :param dataset_names:
        :return:
        """
        active = False

        # if config_name is in any dataset name then config_name is
        # active
        for name in dataset_names:
            if config_name in name:
                active = True
                break

        return active

    def __adc_info(self, adc_name, config_group):
        # 'Raw data + config/SIS 3301' group has only one possible
        # adc ('SIS 3301')
        # adc_info = ( brd,
        #              [chs, ],
        #              {'bit': 14,
        #               'sample rate': (100, 'MHz')})
        adc_info = []

        # conns is a list of tuples where each tuple has the same
        # structure as adc_info
        conns = self.__find_adc_connections(adc_name, config_group)

        for conn in conns:
            conn[2]['bit'] = 14
            conn[2]['sample rate'] = (100.0, 'MHZ')
            adc_info.append(conn)

        return adc_info

    @staticmethod
    def __find_adc_connections(adc_name, config_group):
        conn = []
        brd = None
        chs = []
        for ibrd, board in enumerate(config_group.keys()):
            brd_group = config_group[board]
            for ich, ch_key in enumerate(brd_group.keys()):
                ch_group = brd_group[ch_key]

                if ich == 0:
                    brd = ch_group.attrs['Board']
                    chs = [ch_group.attrs['Channel']]
                else:
                    chs.append(ch_group.attrs['Channel'])

            subconn = (brd, chs,
                       {'bit': None, 'sample rate': (None, 'MHz')})
            conn.append(subconn)

        return conn

    def construct_dataset_name(self, board, channel, *args,
                               config_name=None, return_info=False,
                               **kwargs):
        """
        Returns the name of a HDF5 dataset based on its configuration
        name, board, and channel. Format follows:

            'config_name [brd:ch]'

        :param config_name:
        :param board:
        :param channel:
        :param args:
        :return:
        """
        # TODO: Replace Warnings with proper error handling
        # TODO: Add a Silent kwd

        # assign config_name
        # - if config_name is not specified then the 'active' config
        #   is sought out
        if config_name is None:
            found = 0
            for name in self.data_configs.keys():
                if self.data_configs[name]['active'] is True:
                    config_name = name
                    found += 1

            if found != 1:
                print('** Warning: List of configurations does not have'
                      ' just one active configuration.')
                return None
            else:
                print('** Warning: config_name not specified, assuming '
                      + config_name + '.')

        # ensure all args are valid
        if config_name not in self.data_configs.keys():
            # config_name must be a known configuration
            print('** Warning: Invalid configuration name.')
            return None
        elif self.data_configs[config_name]['active'] is False:
            # if known, config_name must be actively used in the HDF5
            print('** Warning: Configuration is not active.')
            return None
        else:
            # search if (board, channel) combo is connected
            bc_valid = False
            for brd, chs, extras in \
                    self.data_configs[config_name]['SIS 3301']:
                if board == brd:
                    if channel in chs:
                        bc_valid = True

                        # save adc settings for return if requested
                        d_info = extras
                        d_info['adc'] = 'SIS 3301'

            # (board, channel) combo must be active
            if bc_valid is False:
                print('** Warning: (Board, channel) not valid.')
                return None

        # checks passed, build dataset_name
        dataset_name = '{0} [{1}:{2}]'.format(config_name, board,
                                              channel)
        if return_info is True:
            return dataset_name, d_info
        else:
            return dataset_name
