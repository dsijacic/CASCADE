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
#> File name     : tbgen.py                                                     
#> Time created  : Fri Mar 23 12:12:47 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

# if __name__ == '__main__':
#     from handler import Handler, HandlerException
# else:
#     from handlers.handler import Handler, HandlerException

from handler import Handler, HandlerError
from os.path import isfile, exists, join
from generators import *
from os import makedirs
import re

class Port(object):

    def __init__(self, name, width, start, end, direction):
      self.name = name
      self.width = width
      self.start = start
      self.end = end
      self.direction = direction

class TestbenchGenerator(Handler):
    """ TestbenchGenerator assumes that the top module is written in Verilog,
    and that it has clearly defined i/o. 

    module module_name (p1, p2, p3);
    input [7:0] p1;
    input p2;
    output [13:0] p3;
    ...
    endmodule
    """

    PORT_TYPES = ['clk', 'rst', 'exc', 'fin', 'fot', 'key', 'rnd']

    def __init__(self, *generators):
        self.handle = 'tbgen'
        self.help = 'Tesbench generator for logical simulations.'
        self.args = [
            'type', {
                'help': 'Type of frame sequence.',
                'choices': 'edpc devr devu f2all'.split()
            },
            '--force', {
                'help' : 'Force generation of new files.',
                'action': 'store_true'
            },
            '-id', ['test:id'], {
                'help' : 'Unique identifier for the test case.'
            },
            '-tb', ['test:tbfile'], {
                'help': 'Output testbench file.',
            },
            '-tbmodule', ['test:tbmodule'], {
                'help': 'Testbench module name.',
            },
            '-iox', ['analysis:portmap'], {
                'help': 'Output testbench file.',
            },
            '-tr', ['test:trigger'], {
                'help': 'Trigger set to high when SCA should be performed.',
            },
            '-tgt', ['test:target'], {
                'help': 'Target of the SCA evaluation.',
            },
            '-src', ['design:sources:rtl'], {
                'help' : 'CASCADE anotated top module file for active design.',
                'nargs': '+'
            },
            '-ivfile', ['test:ivfile'], {
                'help': 'Output file containing  input vectors.',
            },
            '-kvfile', ['test:kvfile'], {
                'help': 'Key file. Set value to ',
            },
            '-rvfile', ['test:rvfile'], {
                'help': 'External randomness input.',
            },
            '-ivbits', ['test:ivbits'], {
                'help': 'Bits of the input vector.',
                'type': int
            },
            '-ovbits', ['test:ovbits'], {
                'help': 'Bits of the output vector.',
                'type': int
            },
            '-kvbits', ['test:kvbits'], {
                'help': 'Key file. Set value to ',
                'type': int
            },
            '-rvbits', ['test:rvbits'], {
                'help': 'External randomness input.',
                'type': int
            },
            '-tgtbits', ['test:tgtbits'], {
                'help': 'SCA target bits.',
                'type': int
            },
            '-ovector', ['test:ovector'], {
                'help': 'Output vector name in the TB..',
            },
            '-ivector', ['test:ivector'], {
                'help': 'Input vector name in the TB.',
            },
            '-kvector', ['test:kvector'], {
                'help': 'Output vector name in the TB.',
            },
            '-rvector', ['test:rvector'], {
                'help': 'Random vector name in the TB.',
            },
            '-tvector', ['test:tvector'], {
                'help': 'Target vector name in the TB.',
            },
            '-prec', ['simulation:precision'], {
                'help': 'Simulation precision.',
                'choices': '1ps 10ps 100ps 1ns 10ns 100ns'.split(),
            },
            '-nframes', ['simulation:nframes'], {
                'help': 'Number of frames to simulate.',
                'type': int
            },
            '-clk', ['design:clk'], {
                'help': 'Clock signal, only one clock is supported.',
            },
            '-rst', ['design:rst'], {
                'help': 'Reset signal',
            },
            '-rst_level', ['design:rst_level'], {
                'help' : 'Design reset signal.',
                'default' : 0
            },
            '-design', ['design:name'], {
                'help': 'Design name.',
            },
            '-bs', ['analysis:batchsize'], {
                'help': 'Simulation/Analysis batch size. If None (null) everything is processed in one batch.',
                # 'type' : int
            },
            '-sdfstrip', ['simulation:sdf:strip'], {
                'help': 'Path to your design (strip testbench).'
            },
            '-nshares', ['design:nshares'], {
                'help': 'Number of shares.',
                # 'type' : int
            },
            '-rstdelay', ['test:rstdelay'], {
                'help': 'Keep circuit in reset state.',
            },
            '-initdelay', ['test:initdelay'], {
                'help': 'Initial delay not including the reset.',
            },
        ]
        super(TestbenchGenerator, self).__init__(self.handle, self.help, self.args, generators)

    def process(self, root='.'):

        self.update = {}
        self.ports = {}
        self.root = root
        self.parseVerilog()
        self.createInputVectors()
        self.createVerilogTestbench()
        self.createIOXFile()

        return 'Completed testbench generation with id = {}.'.format(self.id), self.update

    def parseVerilog(self):

        bus_re = re.compile('\[(.*)\]')

        src = join(self.root, self.src[0])
        print('Info: Parsing file {} for top source module {}.'.format(src, self.design))

        if not isfile(src):
            raise HandlerError('Source file "{}"not found!'.format(src))
        print('-' * 80)
        print('{:16s} | {:16s} | {:5s} | {:16s}'.format('Port', 'Width', 'Type', 'Range'))
        print('-' * 80)

        sfp = open(src, 'r')

        # start parsing the IO port mapping
        self.ports = {ptype : [] for ptype in TestbenchGenerator.PORT_TYPES}

        for line in sfp:
            line = line.replace(';', '').strip()
            if '/*' in line or '*/' in line:    raise HandlerError('Can not parse "{}". Only // comments are allowed!'.format(src))
            if line[:2] == '//' or line == '':  continue
            line = line.split()

            if line[0] == 'module':
                if line[1] != self.design: raise HandlerError('Wrong design "{}" found in source file "{}". Missmatch with top design "{}"\nMake sure that the top design file is the first in the list of RTL sources.'.format(line[1], src, self.design))

            port_spec = 0
            port_dir = ''
            if line[0] in ['input', 'output']:
                port_dir = line[0]
                if bus_re.match(line[1]):
                    port_name = line[2]
                    port_width = line[1][1:-1].split(':')
                    port_width = int(port_width[0]) - int(port_width[1]) + 1
                    port_spec = 3
                else:
                    port_name = line[1]
                    port_width = 1
                    port_spec = 2

                if '//!' not in line: 
                    raise HandlerError('Invalid port specification. Use //! and then the port spec.')
                port_spec = line[port_spec+1:]
                # port spec parse
                port_type = port_spec[0]
                if port_spec[0] == 'clk':
                    if not (port_name == self.clk and port_width == 1):
                        print('Warning: Invalid clock specified.')
                    port_start = 0
                    port_end = 0
                elif port_spec[0] == 'rst':
                    if not (port_name == self.rst and port_width == 1):
                        print('Warning: Invalid reset specified.')
                    port_start = 0
                    port_end = 0
                else:
                    # try:
                    port_start = int(port_spec[1])
                    port_end = int(port_spec[2])
                    # except:
                    if port_width != port_start - port_end + 1:
                        print('Warning: Port width missmatch on port', port_name)
                        print('Info: Ports must be in big endian.')

                print('{:16s} | {:16d} | {:5s} | {:3d} - {:3d}'.format(port_name, port_width, port_type, port_start, port_end))
                self.ports[port_type].append(Port(port_name, port_width, port_start, port_end, port_dir))

        print('-' * 80)

        # compute bit widths
        ivbits = sum([x.width for x in self.ports['fin']])
        if self.ivbits != ivbits:
            self.update['test:ivbits'] = ivbits
            self.ivbits = ivbits

        ovbits = sum([x.width for x in self.ports['fot']])
        if self.ovbits != ovbits:
            self.update['test:ovbits'] = ovbits
            self.ovbits = ovbits

        kvbits = sum([x.width for x in self.ports['key']])
        if self.kvbits != kvbits:
            self.update['test:kvbits'] = kvbits
            self.kvbits = kvbits

        rvbits = sum([x.width for x in self.ports['rnd']])

        if self.rvbits != rvbits:
            self.update['test:rvbits'] = rvbits
            self.rvbits = rvbits

    def createInputVectors(self):

        # convert None/null to 0
        if not self.bs:
            self.bs = 0

        # runtime
        if self.type == 'edpc':
            edpcfull = 2**(2*self.ivbits) - 2**self.ivbits
            if self.nframes > edpcfull:
                 print('Info: Configured number of frames exceeds the EDPC sequence.')
                 print('Info: Number of frames will be updated.')
                 self.update['simulation:nframes'] = edpcfull
                 self.nframes = edpcfull
            elif self.nframes < edpcfull:
                 print('Info: Configured number of frames {} is smaller than the EDPC sequence {}.'.format(self.nframes, edpcfull))
                 print('Info: Full EDPC sequence is still being dumped to the file.')
                 self.nframes = edpcfull

        if self.ivbits: 
            ivfile = join(self.root, self.ivfile)
            self.getGenerator(self.type, self.ivbits, self.nframes, self.bs, ivfile)

        if self.kvbits: 
            kvfile = join(self.root, self.kvfile)
            if not isfile(kvfile):
                self.getGenerator('devr', self.kvbits, 1, 0, kvfile)
            else:
                print('Info: Selected key file already exists. Refusing to overwrite.')

        if self.rvbits: 
            rvfile = join(self.root, self.rvfile)
            if not isfile(rvfile):
                self.createFile(rvfile)
                self.getGenerator('devr', self.rvbits, self.nframes, self.bs, rvfile)
            else:
                print('Info: Selected radnom file already exists. Refusing to overwrite.')

    def createVerilogTestbench(self):

        tbfile = join(self.root, self.tb)
        ivfile = join(self.root, self.ivfile)
        kvfile = join(self.root, self.kvfile)
        rvfile = join(self.root, self.rvfile)

        if not self.force:
            if isfile(tbfile):
                answer = input('Testbench file already exists. Do you want to overwrite it? [yes/no] ')
                if answer != 'yes':
                    print('Skipped testbench file creation.')
                    return None

        self.createFile(tbfile, '//')

        tb = open(tbfile, 'a')

        # module and parameters
        tb.write('\n')
        if self.ivbits: tb.write('`define IVFILE "{}"\n'.format(ivfile))
        if self.kvbits: tb.write('`define KVFILE "{}"\n'.format(kvfile))
        if self.rvbits: tb.write('`define RVFILE "{}"\n'.format(rvfile))
        tb.write('\n')
        tb.write('module {};\n'.format(self.tbmodule))
        tb.write('\n')
        tb.write('parameter TCLK = -1;\nparameter HTCLK = TCLK/2;\n')
        tb.write('parameter PERIOD = -1;\nparameter HPERIOD = PERIOD/2;\n')
        tb.write('parameter N_FRAMES = -1;\n')
        tb.write('parameter RST_DELAY = -1;\n')
        tb.write('parameter INIT_DELAY = -1;\n')
        tb.write('integer FRAME_CNT  = 0;\n')
        tb.write('integer err;\n')
        tb.write('\n')
        if self.ivbits: tb.write('integer ivfile;\n')
        if self.kvbits: tb.write('integer kvfile;\n')
        if self.rvbits: tb.write('integer rvfile;\n')

        # simulation signals
        tb.write('\n')
        tb.write('reg  SCLK; // simulation clock\n')
        tb.write('reg  {}; // simulation trigger\n'.format(self.tr))
        if self.ivbits == 1:
            tb.write('reg  {};\n'.format(self.ivector))
        else:
            tb.write('reg  [{}:0] {};\n'.format(self.ivbits - 1, self.ivector))
        if self.ovbits == 1:
            tb.write('wire {};\n'.format(self.ovector))
        else:
            tb.write('wire [{}:0] {};\n'.format(self.ovbits - 1, self.ovector))
        if self.rvbits:
            if self.rvbits == 1:
                tb.write('reg {};\n'.format(self.rvector))
            else:
                tb.write('reg [{}:0] {};\n'.format(self.rvbits - 1, self.rvector))
        if self.kvbits:
            if self.kvbits == 1:
                tb.write('reg {};\n'.format(self.kvector))
            else:
                tb.write('reg [{}:0] {};\n'.format(self.kvbits - 1, self.kvector))
        if self.tgtbits == 1:
            tb.write('wire {};\n'.format(self.tvector))
        else:
            tb.write('wire [{}:0] {};\n'.format(self.tgtbits - 1, self.tvector))

        # testbench wires
        tb.write('\n')
        for port in [self.clk, self.rst]:
            tb.write('reg {};\n'.format(port))
        for port in self.ports['key'] + self.ports['exc'] + self.ports['rnd'] + self.ports['fin'] + self.ports['fot']:
            pstr = 'wire '
            if port.width > 1:
                pstr += '[{}:{}] '.format(port.width-1, 0)
            pstr += port.name + ';\n'
            tb.write(pstr)

        # instantiate module
        tb.write('\n')
        tb.write('{} {} (\n'.format(self.design, self.sdfstrip.split('/')[-1]))
        ports = ''
        if self.clk:
            ports += '  .{}({}),\n'.format(self.clk, self.clk)
        if self.rst:
            ports += '  .{}({}),\n'.format(self.rst, self.rst)
        for i in self.ports['exc'] + self.ports['key'] + self.ports['rnd'] + self.ports['fin'] + self.ports['fot']:
            ports += '  .{}({}),\n'.format(i.name, i.name)
        ports = ports[:-2] + '\n);\n'
        tb.write(ports)

        # wire i/o
        tb.write('\n')
        for vec in self.ports['key']:
            if vec.width == self.kvbits:
                tb.write('assign {} = {};\n'.format(vec.name, self.kvector))
                break
            else:
                if vec.start == vec.end:
                    tb.write('assign {} = {}[{}] ;\n'.format(vec.name, self.kvector, vec.start))
                else:
                    tb.write('assign {} = {}[{}:{}];\n'.format(vec.name, self.kvector, vec.start, vec.end))

        for vec in self.ports['rnd']:
            if vec.width == self.rvbits:
                tb.write('assign {} = {};\n'.format(vec.name, self.rvector))
                break
            else:
                if vec.start == vec.end:
                    tb.write('assign {} = {}[{}];\n'.format(vec.name, self.rvector, vec.start))
                else:
                    tb.write('assign {} = {}[{}:{}];\n'.format(vec.name, self.rvector, vec.start, vec.end))

        for vec in self.ports['fin']:
            if vec.width == self.ivbits:
                tb.write('assign {} = {};\n'.format(vec.name, self.ivector))
                break
            else:
                if vec.start == vec.end:
                    tb.write('assign {} = {}[{}];\n'.format(vec.name, self.ivector, vec.start))
                else:
                    tb.write('assign {} = {}[{}:{}];\n'.format(vec.name, self.ivector, vec.start, vec.end))

        for vec in self.ports['fot']:
            if vec.width == self.ovbits:
                tb.write('assign {} = {};\n'.format(self.ovector, vec.name))
                break
            else:
                if vec.start == vec.end:
                    tb.write('assign {} [{}] = {};\n'.format(self.ovector, vec.start, vec.name))
                else:
                    tb.write('assign {} [{}:{}] = {};\n'.format(self.ovector, vec.start, vec.end, vec.name))


        # target as specified in the configuration file
        tb.write('\n')
        tb.write('assign {} = {};\n'.format(self.tvector, self.tgt))

        # driving signals
        tb.write('\n')
        tb.write('always #(HPERIOD) {} = ~ {};\n'.format('SCLK', 'SCLK'))
        if self.clk:
            tb.write('always #(HTCLK) {} = ~ {};\n'.format(self.clk, self.clk))

        # initial
        tb.write('\n')
        tb.write('// read the initial entries\n')
        tb.write('initial begin\n')
        if self.ivbits: 
            tb.write('  ivfile = $fopen(`IVFILE, "rb");\n')     
            tb.write('  err = $fread({}, ivfile);\n'.format(self.ivector))
        if self.kvbits: 
            tb.write('  kvfile = $fopen(`KVFILE, "rb");\n')     
            tb.write('  err = $fread({}, ivfile);\n'.format(self.kvector))
        if self.rvbits: 
            tb.write('  rvfile = $fopen(`RVFILE, "rb");\n')     
            tb.write('  err = $fread({}, ivfile);\n'.format(self.rvector))

        tb.write('\n')
        tb.write('  SCLK = 1\'b1;\n')
        if self.clk:
            tb.write('  {} = 1\'b1;\n'.format(self.clk));

        tb.write('  {} = 0;\n'.format(self.tr))

        if self.rst:
            if self.rst_level == 1:
                on = '1\'b1'
                off = '1\'b0'
            else:
                on = '1\'b0'
                off = '1\'b1'
            tb.write('  {} = {};\n'.format(self.rst, on));
            tb.write('  #(RST_DELAY)\n');
            tb.write('  {} = {};\n'.format(self.rst, off));
        tb.write('  #(INIT_DELAY)\n');
        tb.write('  {} = 1\'b1;\n'.format(self.tr))
        tb.write('\n')
        tb.write('end\n')

        # frame counting and the termination of the testbench
        tb.write('\n')
        tb.write('// read all entries and finish\n')
        tb.write('always @(posedge SCLK) begin\n')
        tb.write('  if (FRAME_CNT >= N_FRAMES) begin\n')
        tb.write('    {} = 0;\n'.format(self.tr))
        tb.write('    $display("Finished %d frames for ID: %s", FRAME_CNT, "{}");\n'.format(self.id))
        tb.write('    $finish;\n')
        tb.write('  end\n')

        tb.write('  if ({}) begin \n'.format(self.tr))
        tb.write('    FRAME_CNT = FRAME_CNT + 1;\n')
        if self.ivbits: 
            tb.write('    err = $fread({}, ivfile);\n'.format(self.ivector))
        if self.rvbits: 
            tb.write('    err = $fread({}, rvfile);\n'.format(self.rvector))
        
        tb.write('  end\n')
        tb.write('end\n')

        # wrap up
        tb.write('\n')
        tb.write('endmodule\n')
        tb.close()

    def createIOXFile(self):

        """ Input/Output/Exclude file. """

        ioxfile = join(self.root, self.iox)
        if not self.force:
            if isfile(ioxfile):
                answer = input('IOX file already exists. Do you want to overwrite it? [yes/no] ')
                if answer != 'yes':
                    print('Skipped IOX file creation.')
                    return None

        self.createFile(ioxfile, '# ')

        fp = open(self.iox, 'a')

    #     for elem in self.vectors['I']:
    #         fp.write('FI {} {}/{}\n'.format(elem[2], self.sdfstrip, elem[0]))
    #     for elem in self.vectors['O']:
    #         fp.write('FO {} {}/{}\n'.format(elem[2], self.sdfstrip, elem[0]))
    #     for elem in self.vectors['C']:
    #         fp.write('EX {} {}/{}\n'.format(elem[2], self.sdfstrip, elem[0]))
    #     for elem in self.vectors['R']:
    #         fp.write('EX {} {}/{}\n'.format(elem[2], self.sdfstrip, elem[0]))
    #     for elem in self.vectors['E']:
    #         fp.write('EX {} {}/{}\n'.format(elem[2], self.sdfstrip, elem[0]))
    #     for elem in self.vectors['I']:
    #         fp.write('EX {} {}/{}\n'.format(elem[2], self.sdfstrip, elem[0]))
    #     # fp.write('EX {} /{}/{}\n'.format(self.ovbits, self.tbmodule, self.ovector))
    #     # fp.write('EX 1 /{}/{}\n'.format(self.tbmodule, self.tr))
    #     fp.write('EX 1 /{}/{}\n'.format(self.tbmodule, self.tgt))
    #     fp.write('TR 1 /{}/{}\n'.format(self.tbmodule, self.tr))

    #     fp.close()
