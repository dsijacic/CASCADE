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
#> File name     : session.py                                                   
#> Time created  : Mon Mar 19 15:05:50 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================
from os.path import join, split, dirname, realpath, exists, relpath, isfile, isdir
from json import dump, load
from shutil import copy
from re import search
from os import makedirs

RAW_REF_PTN = '\$[a-zA-Z0-9:]+'         # raw refferecnce pattern
BRA_REF_PTN = '\$\{[a-zA-Z0-9-_:]+\}';  # braced refference pattern

class SessionManager(object):
    """

    """
    # DATA = join(ROOT, 'data')
    # DEFAULT_SESSION = join(DATA, 'default.json')

    def __init__(self, sessionFile, sessionRoot, defaultConfig):
        self.sessionFile = sessionFile
        self.sessionRoot = sessionRoot
        self.defaultConfig = join(sessionRoot, defaultConfig)
        self.handles = ['init', 'config']
        self.commands = [
            (
                'init', 
                'Initialize a CASCADE session in the current directory.',
                [
                    'design', {
                        'help': 'Design name.'
                    },
                    '-cfg', {
                        'help': 'Target configuration file. If ommited, a default will be created as "design.json".',
                        'default': self.defaultConfig
                    }
                ]
            ),
            (
                'config', 
                'Change the target configuration file.',
                [
                    'cfg', {
                        'help': 'Target configuration file.',
                        'default': None
                    },
                    '--append', {
                        'help': 'Appends the parameters from the specified "cfg" file to the current session.',
                        'action': 'store_true'
                    },
                    '--dump', {
                        'help': 'Current configuration will be dumped to the new "cfg" file.',
                        'action': 'store_true'
                    }
                ]
            )
        ]
        self.updatedParams = {}

    def process(self, command, args):
        targetSession = self.getSession()
        if command == 'init':
            if realpath(targetSession) == join(realpath('.'), self.sessionFile):
                print('Info: Session already exists in current directory:\n -> "{}".'.format(realpath(self.sessionFile)))
            elif targetSession:
                print('Warning: Session found in parent directory:\n -> "{}".'.format(realpath(targetSession)))
                a = input('Do you want to create a nested session? [yes/no] ')
                if a == 'yes':
                    print('Info: Creating a nested session in:\n -> "{}"'.format(realpath('.')))
                    print('Info: Think about it.')
                    self.initSession(args)
                else: 
                    print('Cancelled.')
            else:
                print('Creating session at:\n -> "{}".'.format(realpath(realpath('.'))))
                self.initSession(args)
        else:
            if targetSession:
                if command == 'config':
                    # load session
                    with open(targetSession, 'r') as sf:
                        self.cascadeSession = load(sf)

                    if args['append']:
                        if not isfile(args['cfg']):
                            print('Warning: Adding a non-existing file to the session configuration.')
                            print('Warning: No file found at:\n -> {}'.format(realpath(args['cfg'])))
                        new = relpath(args['cfg'], self.cascadeSession['TOP'])
                        if new not in self.cascadeSession['CFG_FILES']:
                            self.cascadeSession['CFG_FILES'].append(new)
                        else:
                            print('Info: Target session already includes:\n -> {}'.format(realpath(new)))
                            print('Info: Skipped.')
                    elif args['dump']:
                        dumpit = True
                        dumpfp = args['cfg']
                        if isfile(dumpfp):
                            print('Target file already exists.:\n -> {}'.format(realpath(dumpfp)))
                            ack = input('Do you want to overwrite? [yes/no] ')
                            if ack != 'yes':
                                dumpit = False
                        if dumpit:
                            # load parameters
                            self.parameters = {}
                            for cfg in self.cascadeSession['CFG_FILES']:
                                with open(cfg, 'r') as c:
                                    self.parameters.update(load(c))
                            with open(dumpfp, 'w') as df:
                                dump(self.parameters, df, indent=4, sort_keys=True)
                        else:
                            print('Cancelled.')
                    else:
                        updateit = True
                        ack = 'yes'
                        if len(self.cascadeSession['CFG_FILES']) > 1:
                            ack = input('Are you sure you want to replace multiple confuration files\n {} with a single file\n {}? [yes/no] '.format(self.cascadeSession['CFG_FILES'], args['cfg']))
                        if ack != 'yes':
                            updateit = False
                        if updateit:
                            if not isfile(args['cfg']):
                                print('Warning: Configuration file can not be found!\n -> {}'.format(realpath(args['cfg'])))
                            self.cascadeSession['CFG_FILES'] = [args['cfg']]
                    # store session
                    with open(targetSession, 'w') as sf:
                        dump(self.cascadeSession, sf, indent=4, sort_keys=True)
            else:
                print('Error: Session not found in path:\n -> "{}"'.format(realpath('.')))
                print('Error: Call "init" first!')

    def initSession(self, args):
        self.top = realpath('.')
        self.design = args['design']
        if args['cfg'] == self.defaultConfig:
            # default is safely stored in the data folder; make a local copy
            self.cfg = '{}.json'.format(args['design'])
            self.cfg = copy(self.defaultConfig, self.cfg)
            print('Info: Copied default configuration to:\n -> "{}".'.format(realpath(self.cfg)))
        elif not exists(args['cfg']):
            # copies the default configuration into the desired file name
            self.cfg = copy(self.defaultConfig, args['cfg'])
            print('Info: Copied default configuration to:\n -> "{}".'.format(realpath(self.cfg)))
        else:
            # just point to the file
            self.cfg = args['cfg']
            print('Info: Using configuration file:\n -> "{}".'.format(realpath(self.cfg)))
        """ update the session design """
        with open(self.cfg, 'r') as cf:
            self.params = load(cf)
        self.params['design']['name'] = self.design
        with open(self.cfg, 'w') as cf:
            dump(self.params, cf, indent=4, sort_keys=True)

        self.cascadeSession = {
            "TOP" : self.top,
            "CFG_FILES" : [self.cfg]
        }
        with open(self.sessionFile, 'w') as f:
            dump(self.cascadeSession, f, indent=4, sort_keys=True)

        if not isdir(join(self.top, 'src')):
            makedirs(join(self.top, 'src'), 0o700)

    def getSession(self):
        """ probaly could have been implemented using os.path.relpath """
        relativePath = ['.']
        currdir = realpath('.')
        while not exists(join(currdir, self.sessionFile)):
            currdir, prevdir = split(currdir)
            relativePath.append(prevdir)
            if currdir == '/': # no session found up to root
                relativePath.append('/')
                relativePath.reverse()
                relativePath = join(*relativePath[:-1])
                # print('No session found in path: {}'.format(relativePath))
                return ''
        if len(relativePath) > 1:
            relativePath = join(*['..' for _ in relativePath[1:]])
        else:
            relativePath = relativePath[0]
        relativePath = join(relativePath, self.sessionFile)
        return relativePath

    def getSessionRoot(self):
        return self.cascadeSession['TOP']
        
    def loadSession(self):
        # todo: check that parameters are not repeated in files
        targetSession = self.getSession()
        if targetSession:
            with open(targetSession, 'r') as sf:
                self.cascadeSession = load(sf)
            self.parameterfiles = {}
            for cfg in self.cascadeSession['CFG_FILES']:
                try:
                    with open(cfg, 'r') as c:
                        self.parameterfiles[cfg] = load(c)
                except IOError:
                    print('Warning: Configuration file not found!\n -> {}'.format(realpath(cfg)))
            self.parameters = {}
            for cfg, params in self.parameterfiles.items():
                self.parameters.update(params)
            return True
        else:
            print('Error: Can not find active session in path:\n -> {}'.format(realpath('.')))
            return False

    def dumpSession(self):

        # redistribute values to files
        for param, value in self.parameters.items():
            for file, params in self.parameterfiles.items():
                if param in params:
                    self.parameterfiles[file][param] = value

        targetSession = self.getSession()
        for cfg in self.cascadeSession['CFG_FILES']:
            try:
                with open(cfg, 'w') as cf:
                    # SessionManager._display(self.parameterfiles, 0, '++')
                    dump(self.parameterfiles[cfg], cf, indent=4, sort_keys=True)
            except IOError:
                print('Warning: Could not write to configuration file!\n -> {}'.format(realpath(cfg)))
        if targetSession:
            with open(targetSession, 'w') as sf:
                dump(self.cascadeSession, sf, indent=4, sort_keys=True)
        else:
            print('Warning: There is no session to dump.')

    def getFromJson(self, param, startParam):
        """ returns the value of the parameter from json file """
        plevels = param.split(':')
        target = self.parameters
        try:
            for lvl in plevels:
                target = target[lvl]
        except (KeyError, TypeError) as E:
            print('Error:', E)
            print('Warning: Parameter {} can not be dereferenced.'.format(startParam))
            print('Warning: Check configuration files and/or tool swithces.')
            return param
        return target

    def setToJson(self, handle, value, checkHandles):
        """ set parameter with handle to value """
        plevels = handle.split(':')
        target = self.parameters
        try:
            for lvl in plevels[:-1]:
                target = target[lvl]
            target[plevels[-1]] = value
            self.updatedParams[handle] = value
        except KeyError:
            print('Warning: Parameter {} can not be dereferenced. Can not set new value to it.'.format(startParam))
        """ show a warning if the parameter with this handle is referenced """
        if checkHandles:
            self.lookForHandle(handle)

    def derefTarget(self, target, startParam):

        if type(target) == str:
            if '$' in target and    search(BRA_REF_PTN, target) and \
                                    search(RAW_REF_PTN, target):
                print('Warning: Do not mix notations within one parameter!')
                print('BRA_REF_PTN', search(BRA_REF_PTN, target))
                print('RAW_REF_PTN', search(RAW_REF_PTN, target))

            # dereference paramters
            CIRC_DEP_CNT = 0
            while '$' in target:

                CIRC_DEP_CNT += 1
                if CIRC_DEP_CNT >= 1000:
                    print('Error: Circular dependency in a configuration file.')
                    print('Error: Parameter evaluated to {}'.format(target))
                    break

                match = search(BRA_REF_PTN, target)
                if match:

                    match = match.group(0)
                    value = self.getFromJson(match[2:-1], startParam)
                    target = target.replace(match, str(value))

                    continue

                match = search(RAW_REF_PTN, target)
                if match:
                    match = match.group(0)
                    value = self.getFromJson(match[1:], startParam)
                    target = target.replace(match, str(value))
                    continue
        return target

    def getParam(self, param):
        startParam = param
        target = self.getFromJson(param, startParam)
        if type(target) != list:
            target = self.derefTarget(target, startParam)
        else:
            target = [self.derefTarget(t, startParam) for t in target]
        # print('got:', target)
        return target

    def setParam(self, param, value):
        raise NotImplementedError

    def updateParamsFromCLI(self, mapValueDictionary):
        for m, v in mapValueDictionary:
            self.setToJson(m, v, checkHandles=False)

    def update(self, sessionParams):
        """ session params to be updated need to be in map, value tuples """

        for param, value in sessionParams.items():
            # print('@ update:', param,  value)
            try:
                self.setToJson(param, value, checkHandles=True)
            except KeyError:
                print('Warning: Handler added unknown "{}" = "{}" parameter to session.'.format(param, value))
                self.cascadeSession[param] = value

            # if param not in self.parameters.keys():
        #         print('Warning: New parameter "{}" = "{}" added to session.'.format(param, value))
        #         self.cascadeSession[param] = value

        #     else:
        #         # find in which file it belongs
        #         for cfg, params in self.parameterfiles.items():
        #             if param in params.keys():
        #                 self.parameterfiles[cfg][param] = value
        #                 self.parameters[param] = value
        #                 nupdated += 1
        #                 print('Info: Updated parameter "{}" from "{}" to "{}".'.format(param, cfg, value))

        for paramMap, paramValue in self.updatedParams.items():
            print('Info: Parameter "{}" is now set to "{}".'.format(paramMap, paramValue))
        print('Info: Updated {} session parameter(s).'.format(len(self.updatedParams)))

    def _display(d, indent, spacing):
        for k, v in d.items():
            if type(v) != dict:
                print('{}{:30s} {}'.format(indent*spacing, k, v))
            else:
                SessionManager._display(v, indent+1, spacing)

    def display(self, spacing='  '):
        SessionManager._display(self.parameters, 0, spacing)

    def _lookForHandle(paramDict, handle, path):
        handlePaths = []
        for h, v in paramDict.items():
            if type(v) == str:
                if handle in v:
                    handlePaths.append(path + h)
            elif type(v) == dict:
                handlePaths.extend(SessionManager._lookForHandle(v, handle, path + h + ':'))
        return handlePaths


    def lookForHandle(self, handle):
        refHandles = SessionManager._lookForHandle(self.parameters, handle, '')
        for ref in refHandles:
            print('Warning: Parameter with handle "{}" references the updated parameter "{}".'.format(ref, handle))
        if len(refHandles):
            print('Warning: Run the handler again for this update to take place!')

    def getLibraryData(self, libraries):
        handle = self.parameters['lib_id']
        if handle not in libraries:
            raise HandlerError('Can not find library with handle {}.'.format(handle))
        self.parameters['lib'] = libraries[self.parameters['lib_id']]
