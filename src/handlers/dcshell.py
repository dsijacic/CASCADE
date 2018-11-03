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
#> File name     : dcshell.py                                                   
#> Time created  : Mon Jun 25 14:55:30 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from handler import Handler, HandlerError
from os.path import join, isfile
import re

class DcShell(Handler):
    """Design Compiler"""

    def __init__(self):
        self.handle = 'dc'
        self.help = 'Synopsys Design Compiler handler.'
        self.args = [
            '-design', ['design:name'], {
                'help': 'Name of the top level design.',
                'default': None
            },
            '-netlist', ['synthesis:netlist'], {
                'help' : 'Synthesised gate-level netlist.',
                'default' : None
            },
            '-sdf', ['synthesis:sdf'], {
                'help' : 'Standard Delay Format; output.',
                'default' : None
            },
            '-sdc', ['synthesis:sdc'], {
                'help' : 'Synopsys design constraints; output',
                'default' : None
            },
            '-spef', ['synthesis:spef'], {
                'help' : 'SPEF output parasitics.',
                'default' : None
            },
            '-rpt', ['synthesis:rpt'], {
                'help' : 'Synthesis reports.',
                'default' : None
            },
            '-corner', ['design:corner'], {
                'help': 'Synthesis corner.',
                'default': None
            },
            '-sigd', ['synthesis:signifcant_digits'], {
                'help': 'Synthesis corner.',
                'default': None
            },
            '-src', ['design:sources:rtl'], {
                'help': 'Design sources.',
                'default': None,
                'nargs' : '+'
            },
            '-lib', ['lib'], {
                'help': 'All the library information.',
                'default': None
            },
            '-ultra', {
                'help': 'Use the compile_ultra instead of compile',
                'choices' : [None, 'area', 'timing'],
                'default' : None
            },
            '-hold', {
                'help' : 'Keep the dc_shell running.',
                'action' : 'store_true'
            },
            '-tcl', ['synthesis:tcl'], {
                'help' : 'TCL script for synthesis; output.',
                'default' : None
            },
            '-clk', ['design:clk'], {
                'help' : 'Design clock signal.',
                'default' : 'clk_cki'
            },
            '-rst', ['design:rst'], {
                'help' : 'Design reset signal.',
                'default' : 'rst_rbi'
            },
        ]
        super(DcShell, self).__init__(self.handle, self.help, self.args)

    def process(self, root='.'):
        message = ''
        update = {}

        self.prepareFile(self.netlist)
        self.prepareFile(self.sdc)
        self.prepareFile(self.sdf)
        self.prepareFile(self.spef)

        if isfile(self.tcl):
            raise HandlerError('Synthesis script already exists. It may contain many manual modifications. Remove manually to continue.')

        session_path = self.createTclScript(self.tcl, root)
        # print('var: session_path -> {}'.format(session_path))

        fp = open(self.tcl, 'a');
        fp.write('# tool configuration\n')
        fp.write('set power_preserve_rtl_hier_names "true"\n')
        fp.write('set report_default_significant_digits {}\n'.format(self.sigd))
        fp.write('# paths\n')
        fp.write('set lib_path {}\n'.format(self.lib['TOP']))
        fp.write('\n')

        fp.write('# local variables\n')
        fp.write('set design {}\n'.format(self.design))
        # print('var: self.src -> {}'.format(self.src))
        # fp.write('set sources {{{}}}\n'.format(' '.join(self.src)))
        fp.write('set lib_id {}\n'.format(self.lib['handle']))
        fp.write('set lib_name {}\n'.format(self.lib['name']))
        fp.write('\n')

        if self.corner not in self.lib['corners']:
            raise HandlerError('\nTarget corner: {} \
        \nAvailable corners in the target library: {}'.fort(
            self.corner, self.lib['corners']))
        target_library = self.lib['liberty']['ccs']['db'][self.corner]
        fp.write('set target_library $lib_path/{}\n'.format(target_library))
        fp.write('set link_library $target_library\n')
        fp.write('define_design_lib WORK -path ./WORK\n')
        for f in self.src:
            if re.fullmatch('(.*)\.v', f):  
                fp.write('analyze -format verilog $root/{}\n'.format(f))
            elif re.fullmatch('(.*)\.vhd', f):  
                fp.write('analyze -format vhdl    $root/{}\n'.format(f))
            else:
                raise HandlerError('Source file with unkown extension: {}\n'.format(f))
        fp.write('elaborate $design\n')
        fp.write('\n')
        fp.write('# # uncomment to set driving cells on inputs\n')
        fp.write('# set_driving_cell -library $lib_name -lib_cell <DRIVE_CELL> -pin <DRIVE_PIN> [all_inputs]\n')
        if self.rst:
            fp.write('# set_drive 0 [get_ports {}]\n'.format(self.rst))
        if self.clk:
            fp.write('# set_drive 0 [get_ports {}]\n'.format(self.clk))
        fp.write('\n')

        fp.write('# # uncomment to set custom load\n')
        fp.write('# set_load [expr <FANOUT> * [load_of $lib_name/<LOADING_CELL>/<LOADING_PIN>]] [all_outputs]\n')
        fp.write('\n')

        fp.write('# clock signal - set this manually!\n')
        if self.clk:
            fp.write('# create_clock -name {} -period {} {}'.format(self.clk, 111, self.clk))
            fp.write('# set_fix_hold [get_clocks {}]\n'.format(self.clk))
            fp.write('# set_clock_uncertainty {} {}\n'.format(1.11, self.clk))
            fp.write('# set_dont_touch_network [get_clocks {}]\n'.format(self.clk))
        else:
            fp.write('# none')
        fp.write('\n')

        fp.write('# # uncomment to disable all cells, then choose which ones to use\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/*] dont_use true\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/AND2_X*] dont_use false\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/OR2_X*] dont_use false\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/OR2_X*] dont_use false\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/XOR2_X*] dont_use false\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/INV_X*] dont_use false\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/DFF_X*] dont_use false\n')
        fp.write('# set_attribute [get_lib_cells $lib_name/DFFR_X*] dont_use false\n')
        fp.write('\n')

        fp.write('link\n')
        if self.ultra == 'area': 
            fp.write('compile_ultra -use_area_script\n')
        elif self.ultra == 'timing':
            fp.write('compile_ultra -use_timing_script\n')
        else:
            fp.write('compile\n')
        fp.write('check_design\n')
        fp.write('\n')
        
        fp.write('ungroup -all -flatten\n')
        fp.write('change_names -hierarchy -rules verilog -simple_names\n')
        fp.write('write -format verilog -hierarchy -o $root/{}\n'.format(self.netlist))
        fp.write('\n')

        fp.write('# reports\n')
        fp.write('update_timing\n')
        fp.write('write_sdf $root/{}\n'.format(self.sdf))
        fp.write('write_sdc $root/{} -nosplit\n'.format(self.sdc))
        fp.write('write_parasitics -format reduced -output $root/{}\n'.format(self.spef))
        fp.write('write_parasitics -script -format reduced -output $root/{}.tcl\n'.format(self.spef))

        fp.write('report_design  >  $root/{}\n'.format(self.rpt))
        fp.write('report_qor     >> $root/{}\n'.format(self.rpt))
        fp.write('report_cell    >> $root/{}\n'.format(self.rpt))
        fp.write('report_area    >> $root/{}\n'.format(self.rpt))
        fp.write('report_timing  >> $root/{}\n'.format(self.rpt))
        fp.write('\n')

        if not self.hold: 
            fp.write('exit\n')

        fp.close()
        return message, update
