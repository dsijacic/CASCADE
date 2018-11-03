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
#> File name     : cascade.py                                                   
#> Time created  : Fri Jun  1 09:57:35 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from sys        import argv
from time       import time, ctime
from os.path    import dirname, realpath, join
from cli        import CommandLineInterface
from managers   import SessionManager, LibraryManager
from factory    import Factory
from utils      import ppDict

SESSION         = '.cascade'
ROOT            = dirname(realpath(__file__))
DATA            = join(ROOT, '../data')
DEFAULT_CONFIG  = join(DATA, 'default.json')
LIB_DATA_FILE   = join(DATA, 'libraries.json')

cas             = CommandLineInterface()
sesmgr          = SessionManager(SESSION, ROOT, DEFAULT_CONFIG)
libmgr          = LibraryManager(LIB_DATA_FILE)


for cmd in sesmgr.commands: cas.addCommand(*cmd)
for cmd in libmgr.commands: cas.addCommand(*cmd)

libmgr.load()
# print(ppDict(libmgr.libraries))

Factory.create(cas)
cas.parse(argv)

if cas.command in sesmgr.handles:
    sesmgr.process(cas.command, cas.cmdargs)
elif cas.command in libmgr.handles:
    libmgr.process(cas.command, cas.cmdargs)
else:
    if sesmgr.loadSession():
        sesmgr.getLibraryData(libmgr.libraries)

        handler = Factory.get(cas.command)
        parametersThatNeedToBeReadFromConfig, parametersThatWereUpdatedFromCLI \
            = handler.handleCLIArguments(cas.cmdargs)

        if not cas.standalone:
            sesmgr.updateParamsFromCLI(parametersThatWereUpdatedFromCLI)
            sesmgr.getLibraryData(libmgr.libraries)
            # sesmgr.display()
            response = {r :sesmgr.getParam(r) for r in parametersThatNeedToBeReadFromConfig}
            # SessionManager._display(response, 0, '>>')
            handler.updateParamsFromSession(response)
        else:
            print('Info: Starting CASCADE in standalone mode; all parameters must be supplied through CLI.')

        print('Info: {}'.format(handler.help))
        print('Info: Started at {}.'.format(ctime()))
        message = ''
        update = {}
        tstart = time()
        try:
            message, update = handler.process(sesmgr.getSessionRoot())

        # except NotImplementedError as E:
        except Exception as E:
            print('Error:', E)
            message = 'CASCADE encountered an error while executing "{}".'.format(cas.command)
        finally:
            tend = time()
            print('Info: Handler {} finished in {:.3f} seconds with status:'.format(cas.command, (tend - tstart)))
            print('      {}'.format(message))

        if (not cas.standalone) and (not cas.hold):
            print('Info: Updating session.')
            sesmgr.update(update)
            sesmgr.dumpSession()
