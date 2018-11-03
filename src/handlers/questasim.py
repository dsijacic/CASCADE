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
#> File name     : questasim.py                                                 
#> Time created  : Mon Mar 19 10:50:34 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from handler import Handler, HandlerError

from subprocess         import check_output
from os                 import makedirs
from os.path            import split, isdir, realpath, isfile, join

class QuestaSim(Handler):
    """QuestaSim"""
    SOURCE = '~micasusr/design/scripts/questasim_10.6c.rc'
    def __init__(self):
        self.handle = 'vsim'
        self.help = 'MentorGraphics QuestaSim (ModelSim) handler.'
        self.args = [
            'stage', ['<vsimstage>'], {
                'help': 'Stage in the design flow, a separate directory will be created.',
                'choices': ["rtl", "zero", "delta", "fanout", "gln", "par"]
            },
            '-id', ['test:id'], {
                'help' : 'Unique identifier for the test case.'
            },
            '-sdfnoerror', {
                'help' : 'Use -sdfnoerror in modelsim simulation.',
                'action': 'store_true'
            },
            '-novopt_off', {
                'help' : 'Disable -novopt in modelsim simulation.',
                'action': 'store_true'
            },
            '-noglitch', {
                'help' : 'Use -noglitch in modelsim simulation.',
                'action': 'store_true'
            },
            '-design', ['design:name'], {
                'help': 'Name of the top level design.',
                'default': None
            },
            '-tcl', ['vsim:tcl:<vsimstage>'], {
                'help': 'Output TCL file.',
                'default': None
            },
            '-vcd', ['vsim:vcd:<vsimstage>'], {
                'help': 'Output VCD file.',
                'default': None
            },
            '-src', ['design:sources:<vsimstage>'], {
                'help': 'Design sources.',
                'default': None,
                'nargs' : '+'
            },
            '-tb', ['test:tbfile'], {
                'help': 'Testbench file.',
                'default': None
            },
            '-tbmodule', ['test:tbmodule'], {
                'help': 'Testbench module name.',
                'default': None
            },
            '-sdf', ['simulation:sdf:timing:<vsimstage>'], {
                'help': 'SDF file.',
                'default': None
            },
            '-sdfstrip', ['simulation:sdf:strip'], {
                'help': 'Strip path to the core in the SDF file.',
                'default': None
            },
            '-sdfcorner', ['simulation:sdf:corner'], {
                'help': 'Type of the sdf corner.',
                'choices': 'min typ max'.split(),
                'default': None
            },
            '-prec', ['simulation:precision'], {
                'help': 'Simulation precision.',
                'default': None,
                'choices': "1ps 10ps 100ps 1ns 10ns 100ns".split()
            },
            '-tclk', ['simulation:tclk'], {
                'help': 'Design clock period.',
                'default': None,
                'type': int
            },
            '-nclk', ['design:nclk'], {
                'help': 'Number of clock cycles in the design.',
                'default': None,
                'type': int
            },
            '-cpath', ['design:cpath'], {
                'help': 'Critical path of the design.',
                'default': None
            },
            '-nframes', ['simulation:nframes'], {
                'help': 'Number of simulation frames.',
                'type': int,
                'default' : None
            },
            '-tr', ['test:trigger'], {
                'help': 'Trigger signal',
                'default': None
            },
            '-tgt', ['test:tvector'], {
                'help': 'SCA target signal.',
                'default': None
            },
            '-lib', ['lib:functional:<lang>'], {
                'help': 'Functional cell description.',
                'default' : None
            },
            '-lib_top', ['lib:TOP'], {
                'help': 'Location of the library.',
                'default' : None
            },
            '-lang', ['<lang>'], {
                'help': 'Prefered HDL for the library.',
                'default': 'verilog',
                'choices': 'verilog vhdl'.split()
            },
            '-run', {
                'help': 'Simulation runtime.',
                'default' : '-all'
            },
            '-exe', {
                'help': 'Execute the generated script.',
                'action': 'store_true'
            },
            '-rst', ['design:rst'], {
                'help': 'Reset signal.',
            },
            '-rstdelay', ['test:rstdelay'], {
                'help': 'Keep circuit in reset state.',
            },
            '-initdelay', ['test:initdelay'], {
                'help': 'Initial delay not including the reset.',
            },
            '-start', ['test:start'], {
                'help': 'First frame sample.',
            },
            '-finish', ['test:finish'], {
                'help': 'Last frame sample.',
            },
        ]
        super(QuestaSim, self).__init__(self.handle, self.help, self.args)

    def process(self, root):
        message = ''
        update = {}
        self.root = root

        # prepare for output
        vcdfile = join(self.root, self.vcd)
        tclfile = join(self.root, self.tcl)

        self.prepareFile(tclfile)
        self.createFile(tclfile, '# ')
        fp = open(tclfile, 'a');

        fp.write('transcript off\n')

        fp.write('\n')
        fp.write('set root ' + self.root + '\n')
        if self.stage != 'rtl':
            fp.write('set lib_top ' + self.lib_top + '\n')
        fp.write('\n')
        lib = '{}_{}_lib'.format(self.design, self.stage)
        fp.write('vlib {}\n'.format(lib))

        # library resource
        # todo
        if self.stage != 'rtl':
            for libsrc in self.lib:
                if self.lang == 'verilog':
                    fp.write('vlog $lib_top/{} -work {} +time_mode_zero\n'.format(libsrc, lib))
                elif self.lang == 'vhdl':
                    fp.write('vcom $lib_top/{} -work {}\n'.format(libsrc, lib))
                else:
                    raise HandlerError('Unknown HDL {}.'.format(self.lang))

        # sources
        fp.write('\n# sources\n')
        for src in self.src:
            srcfile = join(self.root, src)
            if not isfile(srcfile):
                print('Warning: Source file could not be found on disk!\n -> {}'.format(realpath(src)))
            if src[-2:] == '.v':
                fp.write('vlog $root/{} -work {} +time_mode_zero\n'.format(src, lib))
            elif src[-4:] == '.vhd':
                fp.write('vcom $root/{} -work {}\n'.format(src, lib))
        # tbench
        tbfile = join(self.root, self.tb)
        if not isfile(tbfile):
            print('Warning: Testbench file could not be found on disk!\n -> {}'.format(tbfile))
        if self.tb[-2:] == '.v':
            fp.write('vlog $root/{} -work {}\n'.format(self.tb, lib))
        elif self.tb[-4:] == '.vhd':
            fp.write('vcom $root/{} -work {}\n'.format(self.tb, lib))

        # print (Handler.getTime(self.cpath), self.tclk, self.nclk, Handler.getTime(self.prec))
        if self.tclk * Handler.getTime(self.prec) < Handler.getTime(self.cpath):
            print('Warning: Simulation clock violates critical path of the design.')
            ack = input('Set simulation:tclk to critical path? [yes/no] ')
            if ack == 'yes':
                self.tclk = int(Handler.getTime(self.cpath) / Handler.getTime(self.prec))
                update['simulation:tclk'] = self.tclk
                print('Info: Simulation clock will be updated.')
            else:
                print('Info: Critical path will be violated.')
        period = self.nclk * self.tclk

        rstdelay = period
        initdelay = period
        start = rstdelay + initdelay
        finish = start + self.nframes * period

        if self.rstdelay != rstdelay:
            self.rstdelay = rstdelay
            update['test:rstdelay'] = self.rstdelay
        if self.initdelay != initdelay:
            self.initdelay = initdelay
            update['test:initdelay'] = self.initdelay
        if self.start != start:
            self.start = start
            update['test:start'] = self.start
        if self.finish != finish:
            self.finish = finish
            update['test:finish'] = self.finish

        # run and finish
        fp.write('\n# simulation parameters\n')
        fp.write('vsim {}.{}'.format(lib, self.tbmodule))
        fp.write('\\\n  -t {}'.format(self.prec))
        fp.write('\\\n  -gTCLK={}'.format(self.tclk))               # see tbgen, these generics have fixed names
        fp.write('\\\n  -gPERIOD={}'.format(period))                # see tbgen, these generics have fixed names
        fp.write('\\\n  -gN_FRAMES={}'.format(self.nframes))        # see tbgen, these generics have fixed names
        if self.rst:
            fp.write('\\\n  -gRST_DELAY={}'.format(self.rstdelay))      # see tbgen, these generics have fixed names
        fp.write('\\\n  -gINIT_DELAY={}'.format(self.initdelay))    # see tbgen, these generics have fixed names
        if not self.novopt_off:
            fp.write('\\\n  -novopt')
        if self.noglitch:
            fp.write('\\\n  -noglitch')
        if self.stage not in ['rtl', 'zero']:
            if self.sdfnoerror:
                fp.write('\\\n  -sdfnoerror')
            fp.write('\\\n  -sdf{} {}=$root/{}'.format(self.sdfcorner, self.sdfstrip, self.sdf))
        fp.write('\n')

        fp.write('\n')
        fp.write('onerror {resume}\n')
        fp.write('quietly WaveActivateNextPane {} 0\n')
        fp.write('TreeUpdate [SetDefaultTree]\n')
        fp.write('update\n')

        fp.write('\n# simulation output\n')
        fp.write('vcd file $root/{}\n'.format(self.vcd))
        fp.write('vcd add {}\n'.format(self.tgt))
        fp.write('vcd add {}\n'.format(self.tr))
        fp.write('vcd add {}/*\n'.format(self.sdfstrip))

        fp.write('\n# run and exit\n')
        fp.write('run {}\n'.format(self.run))
        fp.write('quit -sim\n')
        fp.write('quit -f\n')

        # end file
        fp.close()

        message = 'Script created at: ' + tclfile
        if self.exe:
            raise NotImplementedError('Take care of the pipe later')
            # print('Info: Running QuestaSim found at: {}.'.format(QuestaSim.SOURCE))
            # x = check_output('source {}; vsim -c -64 -do {}'.format(
            #     QuestaSim.SOURCE, self.tcl).split()).decode().strip()
            # message = x
        return message, update

