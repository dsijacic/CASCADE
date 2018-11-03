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
#> File name     : primetime.py                                                 
#> Time created  : Mon May  7 16:14:15 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from handler import Handler, HandlerError

from subprocess         import check_output
from os                 import makedirs
from os.path            import split, isdir, realpath, isfile, join

class PrimeTime(Handler):
    """PrimeTime"""
    SOURCE = '/users/micas/micas/design/scripts/primetime_2017.12.rc'
    def __init__(self):
        self.handle = 'pt'
        self.help = 'Synopsys PrimeTime handler.'
        self.args = [
            'stage', ['<ptstage>'], {
                'help': 'Stage in the design flow, a separate directory will be created.',
                'choices': ["gln", "par"]
            },
            '-rcOff', {
                'help' : 'Ignore the RC parasitics from the spef file.',
                'action' : 'store_true'
            },
            '-sdcVersion', {
                'help': 'Version of the SDC file.',
                'default' : '2.0'
            },
            '-id', ['test:id'], {
                'help' : 'Unique identifier for the test case.'
            },
            '-design', ['design:name'], {
                'help': 'Name of the top level design.',
                'default': None
            },
            '-tcl', ['pt_shell:tcl:<ptstage>'], {
                'help': 'Output TCL file.',
                'default': None
            },
            '-out', ['pt_shell:out:<ptstage>'], {
                'help': 'Output OUT file.',
                'default': None
            },
            '-vcd', ['vsim:vcd:<ptstage>'], {
                'help': 'Input VCD file.',
                'default': None
            },
            '-lib', ['lib'], {
                'help': 'All the library information.',
                'default': None
            },
            '-src', ['design:sources:<ptstage>'], {
                'help': 'Target netlist.',
                'default': None,
                'nargs' : '+'
            },
            '-corner', ['design:corner'], {
                'help': 'Synthesis corner.',
                'default': None
            },
            '-sdc', ['par:sdc'], {
                'help' : 'Synopsys design constraints; output',
                'default' : None
            },
            '-rpt', ['par:rpt'], {
                'help' : 'Synthesis reports.',
                'default' : None
            },
            '-sdfstrip', ['simulation:sdf:strip'], {
                'help': 'Strip path to the core in the SDF file.',
                'default': None
            },
            '-spef', ['par:spef'], {
                'help' : 'SPEF input parasitics.',
                'default' : None
            },
            '-exe', {
                'help': 'Execute the generated script.',
                'action': 'store_true'
            }
        ]
        super(PrimeTime, self).__init__(self.handle, self.help, self.args)

    def process(self, root):
        message = ''
        update = {}
        self.root = root

        outfile = join(self.root, self.out)
        tclfile = join(self.root, self.tcl)

        # prepare for output
        self.prepareFile(outfile)
        self.prepareFile(tclfile)

        session_path = self.createTclScript(self.tcl, root)
        fp = open(tclfile, 'a');

        # configure
        fp.write('set lib_path {}\n'.format(self.lib['TOP']))
        target_library = self.lib['liberty']['ccs']['db'][self.corner]
        fp.write('set target_library $lib_path/{}\n'.format(target_library))
        fp.write('set link_path "* $lib_path/{}"\n'.format(target_library))
        fp.write('\n')
        fp.write('set power_enable_analysis true\n')
        fp.write('\n')
        for s in self.src:
            fp.write('read_verilog $root/{}\n'.format(s))
        fp.write('link\n')
        fp.write('current_design {}\n'.format(self.design))

        fp.write('\n')
        fp.write('set power_analysis_mode time_based\n')
        fp.write('read_sdc $root/{} -version {}\n'.format(self.sdc, self.sdcVersion))
        fp.write('read_vcd -strip_path {} $root/{}\n'.format(self.sdfstrip, self.vcd))
        if not self.rcOff:
            fp.write('read_parasitics -format {} -pin_cap_included -verbose {}\n'.format('spef', self.spef))
        fp.write('set_power_analysis_options -waveform_format {} -include top -waveform_output $root/{}\n'.format('out', self.out))
        fp.write('update_timing\n')
        fp.write('update_power\n')
        fp.write('report_power -verbose -hierarchy > $root/{}\n'.format(self.rpt))
        fp.write('report_switching_activity -hierarchy >> $root/{}\n'.format(self.rpt))

        ##########
        # finish #
        ##########
        fp.write('\n')
        fp.write('quit\n')
        fp.close()
        # end file

        message = 'ok'
        if self.exe:
            raise NotImplementedError('take care of pipe later')
            # print('Info: Running QuestaSim found at: {}.'.format(QuestaSim.SOURCE))
            # x = check_output('source {}; vsim -c -64 -do {}'.format(
            #     QuestaSim.SOURCE, self.tcl).split()).decode().strip()
            # message = x
        return message, update

