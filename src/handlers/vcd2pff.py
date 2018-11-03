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
#> File name     : vcd2pff.py                                                   
#> Time created  : Sat Mar 24 18:10:43 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from handler import Handler, HandlerError

from subprocess import check_output
import subprocess
from os import makedirs
from os.path import split, isdir, realpath, isfile

class Vcd2Pff(Handler):
    """ Vcd2Pff """
    BIN = '/users/cosic/dsijacic/Trunk/CASCADE/tools/parsers/vcd2pff/bin/vcd2pff'
    def __init__(self):
        self.handle = 'vcd2pff'
        self.help = 'VCD parser, outputs PFF.'
        self.args = [
            'vcd', {
                'help': 'Target VCD file.',
            },
            '-iox', ['analysis:portmap'], {
                'help': 'Output testbench file.',
            },
            '-o', {
                'help': 'Output PFF file.',
            },
            # '-p', ['simulation:period'], {
            #     'help': 'Simulation period.',
            # },
            '-tclk', ['simulation:tclk'], {
                'help': 'Design clock period.',
            },
            '-nclk', ['design:nclk'], {
                'help': 'Number of clock cycles in the design.',
            },
            '-prec', ['simulation:precision'], {
                'help': 'Simulation precision.',
            },
            '-start', ['test:start'], {
                'help': 'First sample to extract.',
            },
            '-nFrames', ['simulation:nframes'], {
                'help': 'Number of frames to after the first sample.',
            },
            '-trig', ['test:trigger'], {
                'help': 'Name of the trigger signal, take frames only while -trig is 1.',
            },
            '-useTrig', {
                'help': 'Use trigger signal instead of start time.',
                'action': 'store_true'
            },
            '-d', {
                'help': 'Switching distance. msm_power = rising ? 1 : 1 - d.',
                'default': 0.0,
                'type' : float
            },
            '-note', {
                'help': 'Text note for the header.',
                'default': 'CASCADE'
            }
        ]
        super(Vcd2Pff, self).__init__(self.handle, self.help, self.args)

    def process(self, root='.'):

        if not isfile(self.vcd):
            raise HandlerError('Vcd2Pff: Could not find the target VCD file {}'.format(realpath(self.vcd)))

        if not isfile(self.iox):
            raise HandlerError('Vcd2Pff: Could not find the target IOX file {}'.format(realpath(self.iox)))

        if not self.o:
            self.o = self.vcd[:-4] + '.pff'

        self.prec = Handler.getTime(self.prec)
        self.period = self.tclk * self.nclk

        self.prepareFile(self.o)
        
        command = '{} {} {} {} -p {} -d {} -z /'.format(
            self.BIN, 
            self.vcd, 
            self.iox, 
            self.o, 
            self.period, 
            self.d
        )

        if self.useTrig: 
            command += ' -u -t {}'.format(self.trig)
        else:
            command += ' -s {} -f {}'.format(self.start, self.start + self.nFrames * self.period)

        command += ' -N "{}"'.format(self.note)

        update = {}
        try:
            message = check_output(command.split()).decode('utf-8')
        except subprocess.CalledProcessError as e:
            message = 'Command: ' + ' '.join(e.cmd) + '\n Return code: {:02x}'.format(e.returncode)

        message = self.handle + ': \n' + '\n'.join(['\t+ ' + m  for m in message.split('\n')])

        return message, update