#> =============================================================================
#>                     This confidential and proprietary code                   
#>                       may be used only as authorized by a                    
#>                         licensing agreement from                             
#>                     KU Leuven, ESAT Department, COSIC Group                  
#>                    https://securewww.esat.kuleuven.be/cosic/                 
#>                        _____  ____    ____   ____  _____                     
#>                       / ___/ / __ \  / __/  /  _/ / ___/                     
#>                      / /__  / /_/ / _\ \   _/ /  / /__                       
#>                      \___/  \____/ /___/  /___/  \___/                       
#>                                                                              
#>                              ALL RIGHTS RESERVED                             
#>        The entire notice above must be reproduced on all authorized copies.  
#> =============================================================================
#> File name     : library.py                                                   
#> Time created  : Mon Mar 19 15:11:16 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from os.path import isfile
from os.path import split as osplit

from json import load, dump
class LibraryManager(object):

    """ Manages library resources in a centralized manner. """

    def __init__(self, libDataFile):

        self.libDataFile = libDataFile

        self.handles = ['add_lib', 'remove_lib', 'list_lib']
        self.commands = [
            (
                'add_lib',
                'Add a library to the CASCADE library manager.',
                [
                    'handle', {
                        'help' : 'CASCADE handle for the libary.'
                    },
                    'libcfg', {
                        'help' : 'Library configuration file. JSON file in the top directory of the library.'
                    }
                ]
            ),
            (
                'remove_lib',
                'Add a library to the CASCADE library manager.',
                [
                    'handle', {
                        'help' : 'CASCADE handle for the libary.'
                    },
                ]
            ),
            (
                'list_lib',
                'List all handles and locations for the available libraries..',
                [
                    'handle', {
                        'help' : 'CASCADE handle for the libary.'
                    },
                ]
            ),
        ]
    
    def process(self, command, args):
        handle = args['handle']
        libcfg = args['libcfg']

        if not isfile(self.libDataFile):
            raise IOError('Can not find default library storage @ {}!'.format(self.libDataFile))

        with open(self.libDataFile, 'r') as f:
            self.libraries = load(f)

        if command == 'add_lib':
            if handle in self.libraries:
                ack = input('Library with handle {} already exists in CASCADE. Overwrite? [yes/no] '.format(handle))
                if ack != 'yes':
                    print('Canceled by the user.')
                    return None

            if not isfile(libcfg):
                raise IOError('Can not find the library configuration file at {}'.format(libcfgs))
            with open(libcfg, 'r') as f:
                newlib = load(f)
            newlib['TOP'] = osplit(libcfg)[0]

            print('TODO: Control/Enforcing which fields are necessary.')

            self.libraries[handle] = newlib

        elif command == 'remove_lib':
            if handle in self.libraries:
                del self.libraries[handle]
                print('Library with handle {} removed from CASCADE.'.format(handle))
            else:
                print('Library with handle {} not found in CASCADE.'.format(handle))

        elif command == 'list_lib':
            i = 0
            print('{:>3s}. | {:>10s} | {:s}'.format('#', 'Handle', 'Path'))
            for handle, lib in sefl.libraries.items():
                i += 1
                print('{:>3s}. | {:>10s} | {:s}'.format(i, handle, lib[top]))
        else:
            raise Exception('Something went wrong.')

        with open(self.libDataFile, 'w') as f:
            dump(self.libraries, f, indent=4, sort_keys=True)