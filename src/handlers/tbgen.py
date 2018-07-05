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

    def __init__(self, name, width, start, end):
      self.name = name
      self.width = width
      self.start = start
      self.end = end

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
            '-kvfile', ['test:keyfile'], {
                'help': 'Key file. Set value to ',
            },
            '-rvfile', ['test:rndfile'], {
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
            '-kvbits', ['test:keybits'], {
                'help': 'Key file. Set value to ',
                'type': int
            },
            '-rvbits', ['test:rndbits'], {
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
            '-kvector', ['test:keybits'], {
                'help': 'Output vector name in the TB.',
            },
            '-rvector', ['test:rndbits'], {
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
                'default' : 0,
                'type' : int
            },
            '-design', ['design:name'], {
                'help': 'Design name.',
            },
            '-bs', ['analysis:batchsize'], {
                'help': 'Simulation/Analysis batch size. If None (null) everything is processed in one batch.',
            },
            '-sdfstrip', ['simulation:sdf:strip'], {
                'help': 'Path to your design (strip testbench).'
            },
            '-nshares', ['design:nshares'], {
                'help': 'Number of shares.'
            },
        ]
        super(TestbenchGenerator, self).__init__(self.handle, self.help, self.args, generators)

    def process(self, root='.'):

        self.update = {}
        self.ports = {}
        self.root = root
        self.parseVerilog()
        # self.createInputVectors()
        # self.createVerilogTestbench()
        # self.createIOXFile()

        return 'Completed testbench generation with id = {}.'.format(self.id), self.update

    def parseVerilog(self):


        bus_re = re.compile('\[(.*)\]')
        #iox_re = re.compile('//[IOECR]=((\d*):(\d*))|(\d*)')
        
        src = join(self.root, self.src[0])
        print('Info: Parsing file {} for top source module {}.'.format(src, self.design))

        if not isfile(src):
            raise HandlerError('Source file "{}"not found!'.format(src))
        print('-' * 80)
        print('{:16s} | {:16s} | {:5s} | {:16s}'.format('Port', 'Width', 'Type', 'Range'))
        print('-' * 80)

        sfp = open(src, 'r')
        for line in sfp:
            line = line.replace(';', '').strip()
            if '/*' in line or '*/' in line:    raise HandlerError('Can not parse "{}". Only // comments are allowed!'.format(src))
            if line[:2] == '//' or line == '':  continue
            line = line.split()

            if line[0] == 'module':
                if line[1] != self.design: raise HandlerError('Wrong design "{}" found in source file "{}". Missmatch with top design "{}"\nMake sure that the top design file is the first in the list of RTL sources.'.format(line[1], src, self.design))

            # start parsing the IO port mapping
            self.ports = {
              'clk' : [],
              'rst' : [],
              'exc' : [],
              'fin' : [],
              'fot' : [],
              'key' : [],
              'rnd' : [],
            }

            port_spec = 0
            if line[0] in ['input', 'output']:
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
                self.ports[port_type].append(Port(port_name, port_width, port_start, port_end))

        print('-' * 80)

        #     if line[0] == 'input':
        #         iox = line[-1]
        #         if not iox_re.match(iox):
        #             raise HandlerError('Improperly formatted input line!\n\t{}'.format(' '.join(line)))

        #         iox_type = iox[2]
        #         iox_width = iox[4:]

        #         if ':' in iox:
        #             width = line[1].replace('[','').replace(']', '').split(':')
        #             width = int(width[0]) - int(width[1]) + 1
        #             name = line[2].replace(';', '')
        #             position = iox_width.split(':')
        #             position = int(position[0]) - int(position[1]) + 1
        #             if width != position:
        #                 raise HandlerError('Width missmatch in line: {}'.format(' '.join(line)))
        #             position = int(iox_width.split(':')[0])
        #             elem = (name, position, width)
        #         else:
        #             width = 1
        #             name = line[1].replace(';', '')
        #             position = int(iox_width[0])
        #             elem = (name, position, width)

        #         self.vectors[iox_type].append(elem)

        #     if line[0] == 'output':
        #         iox = line[-1]
        #         if not iox_re.match(line[-1]):
        #             raise HandlerError('Improperly formatted output line!\n\t{}'.format(' '.join(line)))

        #         iox_type = iox[2]
        #         iox_width = iox[4:]

        #         if ':' in iox:
        #             width = line[1].replace('[','').replace(']', '').split(':')
        #             width = int(width[0]) - int(width[1]) + 1
        #             name = line[2].replace(';', '')
        #             position = iox_width.split(':')
        #             position = int(position[0]) - int(position[1]) + 1
        #             if width != position:
        #                 raise HandlerError('Width missmatch in line: {}'.format(' '.join(line)))
        #             position = int(iox_width.split(':')[0])
        #             elem = (name, position, width)
        #         else:
        #             width = 1
        #             name = line[1].replace(';', '')
        #             position = int(iox_width[0])
        #             elem = (name, position, width)

        #         self.vectors[iox_type].append(elem)

        # # compute bit widths
        # self.N_I_BITS = sum([elem[2] for elem in self.vectors['I']])
        # if self.N_I_BITS != self.ivbits:
        #     self.update['test:ivbits'] = self.N_I_BITS
        #     self.ivbits = self.N_I_BITS

        # self.N_O_BITS = sum([elem[2] for elem in self.vectors['O']])
        # if self.N_O_BITS != self.ovbits:
        #     self.update['test:ovbits'] = self.N_O_BITS
        #     self.ovbits = self.N_O_BITS

        # if len(self.vectors['C']):
        #     self.CLK = self.vectors['C'][0][0]
        # else:
        #     self.CLK = None
        # if len(self.vectors['R']):
        #     self.RST = self.vectors['R'][0][0]
        # else:
        #     self.RST = None

        # for kw, arg in sorted(self.vectors.items()):
        #     print(kw, arg)

    # def createInputVectors(self):

    #     # runtime
    #     if self.type == 'edpc':
    #         edpcfull = 2**(2*self.ivbits) - 2**self.ivbits
    #         if self.nframes > edpcfull:
    #             print('Info: Configured number of frames exceeds the EDPC sequence.')
    #             print('Info: Number of frames will be updated.')
    #             self.update['simulation:nframes'] = edpcfull
    #             self.nframes = edpcfull
    #         elif self.nframes < edpcfull:
    #             print('Info: Configured number of frames {} is smaller than the EDPC sequence {}.'.format(self.nframes, edpcfull))
    #             print('Info: Full EDPC sequence is still being dumped to the file.')
    #             self.nframes = edpcfull

    #     if self.ivbits: 
    #         self.createFile(self.ivfile)
    #         self.getGenerator(self.type, self.ivbits, self.nframes, self.bs, self.ivfile)
    #     if self.kvbits: 
    #         if not isfile(self.kvfile):
    #             self.createFile(self.kvfile)
    #             self.getGenerator('devr', self.kvbits, 1, self.kvfile)
    #         else:
    #             print('Info: Selected key file already exists. Refusing to overwrite.')
    #     if self.rvbits: 
    #         if not isfile(self.rvfile):
    #             self.createFile(self.rvfile)
    #             self.getGenerator('devr', self.kvbits, self.nframes, self.bs, self.rvfile)
    #         else:
    #             print('Info: Selected randomness file already exists. Refusing to overwrite.')

    # def createVerilogTestbench(self):
    #     self.tb = join(self.root, self.tb)
    #     if not self.force:
    #         if isfile(self.tb):
    #             answer = input('Testbench file already exists. Do you want to overwrite it? [yes/no] ')
    #             if answer != 'yes':
    #                 print('Skipped testbench file creation.')
    #                 return None

    #     self.createFile(self.tb, '//')

    #     tb = open(self.tb, 'a')

    #     # module and parameters
    #     tb.write('// ---\n')
    #     if self.ivbits: tb.write('`define IVFILE "{}"\n'.format(self.ivfile))
    #     if self.kvbits: tb.write('`define KVFILE "{}"\n'.format(self.kvfile))
    #     if self.rvbits: tb.write('`define RVFILE "{}"\n'.format(self.rvfile))
    #     tb.write('// ---\n')
    #     tb.write('module {};\n'.format(self.tbmodule))
    #     tb.write('// ---\n')
    #     tb.write('parameter TCLK = -1;\nparameter HTCLK = TCLK/2;\n')
    #     tb.write('parameter PERIOD = -1;\nparameter HPERIOD = PERIOD/2;\n')
    #     tb.write('parameter N_FRAMES = -1;\n')
    #     tb.write('integer FRAME_CNT  = 0;\n')
    #     tb.write('integer err;\n')

    #     if self.ivbits: tb.write('integer ivfile;\n');
    #     if self.kvbits: tb.write('integer kvfile;\n');
    #     if self.rvbits: tb.write('integer rvfile;\n');
        

    #     # simulation signals
    #     tb.write('// ---\n')
    #     tb.write('reg  SCLK; // simulation clock\n')
    #     tb.write('reg  {}; // simulation trigger\n'.format(self.tr))
    #     if self.ivbits == 1:
    #         tb.write('reg  {};\n'.format(self.ivector))
    #     else:
    #         tb.write('reg  [{}:0] {};\n'.format(self.ivbits - 1, self.ivector))
    #     if self.ovbits == 1:
    #         tb.write('wire {};\n'.format(self.ovector))
    #     else:
    #         tb.write('wire [{}:0] {};\n'.format(self.ovbits - 1, self.ovector))
    #     if self.tgtbits == 1:
    #         tb.write('wire {};\n'.format(self.ivector))
    #     else:
    #         tb.write('wire [{}:0] {};\n'.format(self.tgtbits - 1, self.tvector))

    #     # self.N_OV_BITS = self.N_O_BITS // self.nshares
    #     # if self.N_O_BITS % self.nshares:
    #     #     raise HandlerError('Incompatible number of shares {} for {} output bits.'.format(self.nshares, self.N_O_BITS))
    #     # if self.N_OV_BITS == 1:
    #     #     tb.write('wire {};\n'.format(self.ovector))
    #     # else:
    #     #     tb.write('wire [{}:0] {};\n'.format(self.N_OV_BITS - 1, self.ovector))

    #     # wire i/o
    #     tb.write('// ---\n')
    #     for io in self.vectors['I'] + self.vectors['O']:
    #         name = io[0]
    #         position = io[1]
    #         width = io[2]
    #         if width == 1:
    #             tb.write('wire {};\n'.format(name))
    #         else:
    #             tb.write('wire [{}:{}] {};\n'.format(width-1, 0, name))
    #     for ee in self.vectors['E']:
    #         name = ee[0]
    #         position = ee[1]
    #         width = ee[2]
    #         if width == 1:
    #             tb.write('reg {};\n'.format(name))
    #         else:
    #             tb.write('reg [{}:{}] {};\n'.format(width-1, 0, name))
    #     if self.CLK or self.RST:
    #         tb.write('// ---\n')
    #     if self.CLK != None:
    #         tb.write('reg {};\n'.format(self.CLK))
    #     if self.RST != None:
    #         tb.write('reg {};\n'.format(self.RST))

    #     # instantiate module
    #     tb.write('// ---\n')
    #     tb.write('{} {} (\n'.format(self.design, self.sdfstrip.split('/')[-1]))
    #     ports = ''
    #     if self.CLK != None:
    #         ports += '  .{}({}),\n'.format(self.CLK, self.CLK)
    #     if self.RST != None:
    #         ports += '  .{}({}),\n'.format(self.RST, self.RST)
    #     for i in self.vectors['I']:
    #         i = i[0]
    #         ports += '  .{}({}),\n'.format(i, i)
    #     for o in self.vectors['O']:
    #         o = o[0]
    #         ports += '  .{}({}),\n'.format(o, o)
    #     for e in self.vectors['E']:
    #         e = e[0]
    #         ports += '  .{}({}),\n'.format(e, e)
    #     ports = ports[:-2] + '\n);\n'
    #     tb.write(ports)

    #     # wire inputs
    #     tb.write('// ---\n')
    #     for i in self.vectors['I']:
    #         name = i[0]
    #         position = i[1]
    #         width = i[2]
    #         if width == 1:
    #             if self.N_I_BITS == 1:
    #                 tb.write('assign {} = {};\n'.format(name, self.ivector))
    #                 break
    #             else:
    #                 tb.write('assign {} = {}[{}];\n'.format(name, self.ivector, position))
    #         else:
    #             if self.N_I_BITS == 1:
    #                 raise Tbgen('This should not happen.')
    #             else:
    #                 tb.write('assign {} = {}[{}:{}];\n'.format( \
    #                     name, self.ivector, position, position - width + 1))
    #     tb.write('// ---\n')

    #     for o in self.vectors['O']:
    #         name = o[0]
    #         position = o[1]
    #         width = o[2]
    #         if width == 1:
    #             if self.N_O_BITS == 1:
    #                 tb.write('assign {} = {};\n'.format(self.ovector, name))
    #             else:
    #                 tb.write('assign {}[{}] = {};\n'.format(self.ovector, position, name))
    #         else:
    #             if self.N_O_BITS == 1:
    #                 raise Tbgen('This should not happen.')
    #             else:
    #                 tb.write('assign {}[{}:{}] = {};\n'.format( \
    #                     self.ovector, position, position - width + 1, name))
    #     # target as specified in the configuration file
    #     tb.write('assign {} = {};\n'.format(self.tvector, self.tgt))
    #     tb.write('// ---\n')
    #     # driving signals
    #     if self.CLK != None:
    #         tb.write('always #(HTCLK) {} = ~ {};\n'.format(self.CLK, self.CLK))
    #     tb.write('always #(HPERIOD) {} = ~ {};\n'.format('SCLK', 'SCLK'))

    #     # initial
    #     tb.write('// --- read initial entries\n')
    #     tb.write('initial begin\n')
    #     if self.ivbits: 
    #         tb.write('  ivfile = $fopen(`IVFILE, "rb");\n')     
    #         tb.write('  err = $fread({}, ivfile);\n'.format(self.ivector))
    #     if self.kvbits: 
    #         tb.write('  kvfile = $fopen(`KVFILE, "rb");\n')     
    #         tb.write('  err = $fread({}, ivfile);\n'.format(self.kvector))
    #     if self.rvbits: 
    #         tb.write('  rvfile = $fopen(`RVFILE, "rb");\n')     
    #         tb.write('  err = $fread({}, ivfile);\n'.format(self.rvector))

    #     tb.write('  SCLK = 1\'b1;\n')
    #     if self.CLK != None:
    #         tb.write('  {} = 1\'b1;\n'.format(self.CLK));
    #     tb.write('  {} = 0;\n'.format(self.tr))
    #     # if there is a RST signal use one PERIOD time to properly reset the circuit
    #     # 1*TCLK would do just fine as well
    #     if self.RST != None:
    #         tb.write('  {} = 1\'b0;\n  #(PERIOD) {} = 1\'b1;\n'.format(self.RST, self.RST));
    #     # another PERIOD for the initial state to propagatet properly, then start the high trigger
    #     tb.write('  #(PERIOD) {} = 1\'b1;\n'.format(self.tr))
    #     tb.write('end\n')

    #     # frame counting and the termination of the testbench
    #     tb.write('// --- read all entries ---\n')
    #     tb.write('always @(posedge SCLK) begin\n')
    #     tb.write('  if (FRAME_CNT >= N_FRAMES) begin\n')
    #     tb.write('    {} = 0;\n'.format(self.tr))
    #     tb.write('    $display("Finished %d frames for ID: %s", FRAME_CNT, "{}");\n'.format(self.id))
    #     tb.write('    $finish;\n')
    #     tb.write('  end\n')

    #     tb.write('  if ({}) begin \n'.format(self.tr))
    #     tb.write('    FRAME_CNT = FRAME_CNT + 1;\n')
    #     tb.write('    err = $fread({}, ivfile);\n'.format(self.ivector))
    #     tb.write('  end\n')
    #     tb.write('end\n')

    #     # wrap up
    #     tb.write('// ---\n')
    #     tb.write('endmodule\n')
    #     tb.close()

    # def createIOXFile(self):

    #     """ Input/Output/Exclude file. """
    #     if not self.force:
    #         if isfile(self.iox):
    #             answer = input('IOX file already exists. Do you want to overwrite it? [yes/no] ')
    #             if answer != 'yes':
    #                 print('Skipped IOX file creation.')
    #                 return None

    #     self.createFile(self.iox, '# ')
    #     fp = open(self.iox, 'a')

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
