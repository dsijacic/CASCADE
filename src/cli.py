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
#> File name     : cli.py                                                       
#> Time created  : Mon Mar 19 10:54:18 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

class CommandLineInterface(object):
    """
    Common interface for the CASCADE framework.
    """

    def __init__(self):
        self.handles = []
        self.parser = ArgumentParser(\
            description='Computer Aided Side Channel Analysis Design Environment',\
            formatter_class=RawTextHelpFormatter)
        self.toplvlopts = self.parser.add_mutually_exclusive_group()
        self.toplvlopts.add_argument('--standalone', action='store_true',\
            help='Skips the parameter exchange with the environment. Handlers process which ever (default) arguments they may have.')
        self.toplvlopts.add_argument('--hold', action='store_true',\
            help='Hold the old values in the configuration file, skip the update.')
        self.cmdParsers = self.parser.add_subparsers()
        self.standalone = None
        self.hold = None
        self.command = None
        self.cmdargs = None

    def addCommand(self, handle, help, args):
        """ 
        Arguments should be supplied as a list:
        {name|-name|--name}, \{name: value\}
        e.g.
        args = [
            'design', {
                'help' : 'Design name.'
            },
            '-cfg', {
                'help': 'Configuration file.', 
                'default': None
            }
        ]
        """
        self.handles.append(handle)
        setattr(self, handle+'Parser', self.cmdParsers.add_parser(handle, help=help))
        argHandles = []
        mapHelp = ''
        for arg in args:
            if type(arg) == str:
                argHandles.append(arg)
            elif type(arg) == dict:
                if 'help' in arg:
                    arg['help'] = mapHelp + '\n' + arg['help']
                getattr(self, handle+'Parser').add_argument(*argHandles, **arg)
                argHandles = []
                mapHelp = ''
            elif type(arg) == list:
                mapHelp = str(arg)
            else:
                print('Can not add "{}" to CLI. Invalid arguments: "{}"'.format(argHandles, args))
        
    def parse(self, args):
        args = args[1:]
        if len(args) < 1:
            self.parser.parse_args(['-h'])
        else:
            if args[0] in ['--standalone', '--hold']:
                self.command = args[1]
            else:
                self.command = args[0]
            self.cmdargs = vars(self.parser.parse_args(args))
            self.standalone = self.cmdargs['standalone']; del self.cmdargs['standalone']
            self.hold = self.cmdargs['hold']; del self.cmdargs['hold']

