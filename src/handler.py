# -*- coding: utf-8 -*-
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
#> File name     : handler.py                                                   
#> Time created  : Mon Mar 19 10:50:41 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

DEBUG_TRACE = False

import re

IS_SWITCH_RE = re.compile('<[a-zA-Z0-9_-]*>$')
CONTAINS_SWITCH_RE = re.compile('(.*)<[a-zA-Z0-9_-]*>(.*)')
SWITCH_PATTERN = '<[a-zA-Z0-9_-]*>'

from getpass import getuser
from time import ctime
from socket import gethostname
from os.path import join, split, realpath, relpath, isdir
from os import makedirs

class Option(object):

    def __init__(self, handle, argdict):
        self.handle = handle
        while self.handle[0] == '-':
            self.handle = self.handle[1:]

        self.default = None
        if 'default' in argdict:
            self.default = argdict['default']
        elif 'action' in argdict:
            if argdict['action'] == 'store_true':
                self.default = False
            elif argdict['action'] == 'store_false':
                self.default = True
        self.type = str
        if 'type' in argdict:
            self.type = argdict['type']
        self.value = self.default

class Parameter(Option):

    COLLECTION = []

    def __init__(self, handle, cfgmap, argdict):
        super(Parameter, self).__init__(handle, argdict)
        self.cfgmap = cfgmap
        Parameter.COLLECTION.append(self)

    def getMapping(self):
        """ 
        Parameters that are not switches <switch>, and that are not 
        altered from the CLI (none default), need to be mapped to configuration
        parameters from the active session.
        returns:
            mapping - mapping to configuration file if one exists (None for <switches>)
            updated - True if the value has been updated from CLI
        """
        if IS_SWITCH_RE.match(self.cfgmap):
            return None, None
        # elif self.value != self.default:
        #     return None, self.
        else:
            """removes switches from the mapping, so an actual map value can be 
            passed"""
            mapping = self.cfgmap
            while CONTAINS_SWITCH_RE.match(mapping):
                switch = re.search(SWITCH_PATTERN, mapping).group(0)
                for param in Parameter.COLLECTION:
                    if param.cfgmap == switch:
                        mapping = mapping.replace(switch, param.value)
                        break
            updated = False
            if self.value != self.default:
                updated = True 

            return mapping, updated

        

class HandlerError(Exception):
    """ Handler errors. """

class Handler(object):
    """
    Generic handler wrapper for CASCADE.
    """
    def __init__(self, handle, help, args, *generators):
        self.handle = handle
        self.help = help
        self.args = args
        self.generators = generators
        if len(self.generators):
            self.generators = self.generators[0]
        self.paramCollection = []
        self.options = []

        handle = None
        cfgmap = None
        argdict = None
        for arg in args:
            if type(arg) == str: 
                handle = arg
            elif type(arg) == list:
                cfgmap = arg[0]
            elif type(arg) == dict:
                argdict = arg
                if handle and cfgmap and argdict:
                    self.paramCollection.append(Parameter(handle, cfgmap, argdict))
                elif handle and argdict:
                    self.options.append(Option(handle, argdict))
                handle = None
                cfgmap = None
                argdict = None
            else:
                print('Error: Invalid argument format.')
                print('Error: handle = {}'.format(handle))
                print('Error: cfgmap = {}'.format(cfgmap))
                print('Error: argdict = {}'.format(handle))

        self.paramCollection = {p.handle: p for p in self.paramCollection}
        self.options = {o.handle: o for o in self.options}

    def getGenerator(self, handle, *args):
        # print(args)
        for g in self.generators:
            if g.handle == handle:
                return g.generate(*args)
        raise HandlerError('Unknown generator handle "{}".'.format(handle))

    def handleCLIArguments(self, cliArgs):
        
        """1. Get arguments from command line, and assign them where needed. """
        for arg, value in cliArgs.items():
            # print('arg, value:', arg, value)
            if arg in self.options.keys():
                self.options[arg].value = value
            elif arg in self.paramCollection.keys():
                self.paramCollection[arg].value = value
            else:
                print('Warning: Unkown argument passed from command line interface.')
                print('Warning: {} = {} is ignored.'.format(arg, value))

        """2. Create class data members for easier handling. """
        for handle, opt in self.options.items(): 
            setattr(self, opt.handle, opt.value)
        for handle, param in self.paramCollection.items():
            setattr(self, param.handle, param.value)

        """3. For arguments that have not been changed from CLI request values
        using their mapping. """
        parametersThatNeedToBeReadFromConfig = []
        parametersThatWereUpdatedFromCLI = []
        for handle, param in self.paramCollection.items():
            mapping, updated = param.getMapping()
            if mapping:
                if updated:
                    parametersThatWereUpdatedFromCLI.append((mapping, param.value))
                else:
                    parametersThatNeedToBeReadFromConfig.append(mapping)

        return parametersThatNeedToBeReadFromConfig, parametersThatWereUpdatedFromCLI

    def getTime(timeStr):
        if not re.match('(\d*)[pnum]s', timeStr):
            raise HandlerError('Improperly formatted time value "{}" found.'.format(timeStr))
        time2float = {
            'ps' : 1e-12,
            'ns' : 1e-9,
            'us' : 1e-6,
            'ms' : 1e-3
        }
        return float(timeStr[:-2]) * time2float[timeStr[-2:]]
        
    def prepareFile(self, filepath):
        """ Prepare file for creation (create directory and get its absolute 
        path """
        path = realpath(filepath)
        tgtdir, tgtfile = split(path)
        if not isdir(tgtdir):
            makedirs(tgtdir, 0o700)
        return realpath(filepath)

    def _createFile(self, filepath):
        path = self.prepareFile(filepath)
        tgtdir, tgtfile = split(path)
        try:
            fp = open(filepath, 'w')
            fp.close()
            return path
        except IOError:
            print('Error: Can not open file {} for writting.'.format(realpath(filepath)))
            return False

    def createFile(self, filepath, comment='# '):
        if self._createFile(filepath):
            fp = open(filepath, 'a')
            fp.write(self.cosic(comment))
            fp.close()

    def createTclScript(self, filepath, root):
        if self._createFile(filepath):
            fp = open(filepath, 'a')
            # paths relative to the directory where it was invoked.
            fp.write(self.cosic('# '))
            fp.write('\nset root {}\n\n'.format(root))
            fp.close()
            return 'root'
        else:
            return None

    def includeFile(self, filepath):
        """ gets a relative path to file """
        path = realpath(filepath)
        if not isfile(path):
            print('Warning: File {} not found on disk!'.format(path))
        return relpath(filepath)

    def updateParamsFromSession(self, response):
        """ Update values as per the data from the configuration files. """
        for cfgmap, value in response.items():
            # print('>>>>>', cfgmap, value)
            for handle, param in self.paramCollection.items():
                mapping, updated = param.getMapping()
                if mapping and cfgmap == mapping:
                # if cfgmap == param.getMapping():
                    self.paramCollection[handle].value = value
                    if self.paramCollection[handle].type != str:
                        value = self.paramCollection[handle].type(value)
                    setattr(self, handle, value)
                    break

    def cosic(self, comment ='# '):
        cstr = [
            '==============================================================================',
            '=                    This confidential and proprietary code                  =',
            '=                      may be used only as authorized by a                   =',
            '=                        licensing agreement from                            =',
            '=                    KU Leuven, ESAT Department, COSIC Group                 =',
            '=                   https://securewww.esat.kuleuven.be/cosic/                =',
            '=                       _____  ____    ____   ____  _____                    =',
            '=                      / ___/ / __ \  / __/  /  _/ / ___/                    =',
            '=                     / /__  / /_/ / _\ \   _/ /  / /__                      =',
            '=                     \___/  \____/ /___/  /___/  \___/                      =',
            '=                                                                            =',
            '=                             ALL RIGHTS RESERVED                            =',
            '=       The entire notice above must be reproduced on all authorized copies. =',
            '=                                                                            =',
            '=               Danilo Sijacic <danilo.sijacic@esat.kuleuven.be>             =',
            '==============================================================================',
            '{} CASCADE [{}] by {}@{}'.format(ctime()[4:], self.handle, getuser(), gethostname()),
            '=============================================================================='
        ]

        cstr = [comment + c for c in cstr]

        return '\n'.join(cstr) + '\n'

    def process(self, root='.'):
        print('Virtual generic handler.')
        raise NotImplementedError

