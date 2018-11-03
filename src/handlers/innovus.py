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
#> File name     : innovus.py                                                   
#> Time created  : Wed Sep 26 15:52:29 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from handler import Handler, HandlerError
from os.path import join, isfile
import re

class Innovus(Handler):
    """ Innovus handler """

    def __init__(self):
        self.handle = 'par'
        self.help = 'Cadence Innovus Hanler.'
        self.args = [
            '-design', ['design:name'], {
                'help': 'Name of the top level design.',
                'default': None
            },
            '-mmmc', ['par:mmmc'], {
                'help' : 'Multi-corner analysis timing file.'
            },
            '-mmmcSource', ['lib:backend:mmmc'], {
                'help' : 'Library etalon for the mmmc file.'
            },
            '-library', ['lib:TOP'], {
                'help' : 'Top directory for the library.'
            },
            '-lef', ['lib:backend:lef_files'], {
                'help' : 'LEF geometries.'
            },
            '-site', ['par:site'], {
                'help' : 'Floorplan site.'
            },
            '-parNetlist', ['par:netlist'], {
                'help' : 'PAR netlist.',
            },
            '-parSpef', ['par:spef'], {
                'help' : 'Extracted parasitics from the layout.'
            },
            '-parSdc', ['par:sdc'], {
                'help' : 'Timing contraints.'
            },
            '-parSdf', ['par:sdf'], {
                'help' : 'Timing contraints.'
            },
            '-parRpt', ['par:rpt'], {
                'help' : 'Timing report.'
            },
            '-aspectRatio', ['par:floorPlan:aspectRatio'], {
                'help' : 'Ascpect ratio of the floorPlan.',
                'default' : '1.0'
            },
            '-density', ['par:floorPlan:density'],{
                'help' : 'Density of the floorPlan.',
                'default' : '0.7'
            },
            '-fromEdge', ['par:floorPlan:fromEdge'], {
                'help' : 'Margin of the floorPlan.',
                'default' : '3.0'
            },
            '-topMetalLayer', ['lib:backend:topMetalLayer'], {
                'help' : 'Power rings stack.',
                'default' : 'metal10'
            },
            '-pwrRingWidth', ['par:pwrRing:width'], {
                'help' : 'addRing width',
            },
            '-pwrRingSpacing', ['par:pwrRing:spacing'], {
                'help' : 'addRing spacing',
            },
            '-pwrRingOffset', ['par:pwrRing:offset'], {
                'help' : 'addRing offset',
            },
            '-pwr', ['lib:backend:pwr'], {
                'help' : 'Power rail in the library.'
            },
            '-gnd', ['lib:backend:gnd'], {
                'help' : 'Ground rail in the library.'
            },
            '-netlist', ['synthesis:netlist'], {
                'help' : 'Synthesised gate-level netlist.',
            },
            '-processNode' , ['lib:backend:processNode'], {
                'help' : 'Size othe technology node in nm.'
            },
            '-libBuffers', ['lib:backend:buffers'], {
                'help': 'Collection of buffers for skew correction.'
            },
            '-libFillers', ['lib:backend:fillers'], {
                'help': 'Collection of physical filler cells.'
            },
            '-clk', ['design:clk'], {
                'help' : 'Design clock.'
            },
            '-sdc', ['synthesis:sdc'], {
                'help' : 'Synopsys design constraints; output',
            },
            '-scripts', ['par:scripts'], {
                'help' : 'Directory for generated PAR scripts.',
            },
            '-captables', ['lib:backend:captables'], {
                'help' : 'Capacitance tables of the library.'
            },
            '-libPVTMin', ['lib:backend:pvt:min'], {
                'help' : 'Temperature of a corner.'
            },
            '-libPVTTyp', ['lib:backend:pvt:typ'], {
                'help' : 'Temperature of a corner.'
            },
            '-libPVTMax', ['lib:backend:pvt:max'], {
                'help' : 'Temperature of a corner.'
            },
            '-libLibMin', ['lib:liberty:ccs:lib:min'], {
                'help' : 'Library file of the corner.'
            },
            '-libLibTyp', ['lib:liberty:ccs:lib:typ'], {
                'help' : 'Library file of the corner.'
            },
            '-libLibMax', ['lib:liberty:ccs:lib:max'], {
                'help' : 'Library file of the corner.'
            },
            '-setExtractRCMode_engine', {
                'choices' : ['postRoute'],
                'default' : 'postRoute'
            },
            '-setExtractRCMode_effortLevel', {
                'choices' : ['low'],
                'default' : 'low'
            },
            '-setExtractRCMode_coupled', {
                'choices' : ['true', 'false'],
                'default' : 'false'
            }

        ]
        super(Innovus, self).__init__(self.handle, self.help, self.args)

    def createMMMC(self):

        mmmcFile = ''
        mmmcFile += '# Version:1.0 MMMC View Definition File\n'
        mmmcFile += '# Do Not Remove Above Line\n'  
        mmmcFile += '# Generated by CASCADE\n'
        mmmcFile += '### rc_corners ###\n'
        mmmcFile += 'create_rc_corner -name rc_bc \\\n-cap_table {}/{} \\\n-T {} -preRoute_res {{1.0}} -preRoute_cap {{1.0}} -preRoute_clkres {{0.0}} -preRoute_clkcap {{0.0}} -postRoute_res {{1.0}} -postRoute_cap {{1.0}} -postRoute_xcap {{1.0}} -postRoute_clkres {{0.0}}\n'.format(self.library, self.captables, self.libPVTMin[2])
        mmmcFile += 'create_rc_corner -name rc_tc \\\n-cap_table {}/{} \\\n-T {} -preRoute_res {{1.0}} -preRoute_cap {{1.0}} -preRoute_clkres {{0.0}} -preRoute_clkcap {{0.0}} -postRoute_res {{1.0}} -postRoute_cap {{1.0}} -postRoute_xcap {{1.0}} -postRoute_clkres {{0.0}}\n'.format(self.library, self.captables, self.libPVTTyp[2])
        mmmcFile += 'create_rc_corner -name rc_wc \\\n-cap_table {}/{} \\\n-T {} -preRoute_res {{1.0}} -preRoute_cap {{1.0}} -preRoute_clkres {{0.0}} -preRoute_clkcap {{0.0}} -postRoute_res {{1.0}} -postRoute_cap {{1.0}} -postRoute_xcap {{1.0}} -postRoute_clkres {{0.0}}\n'.format(self.library, self.captables, self.libPVTMax[2])
        mmmcFile += '### op_conds ###\n'
        mmmcFile += 'create_op_cond -name op_bc\\\n -library_file {}/{} \\\n-P {} -V {} -T {}\n'.format(self.library, self.libLibMin, self.libPVTMin[0], self.libPVTMin[1], self.libPVTMin[2])
        mmmcFile += 'create_op_cond -name op_tc\\\n -library_file {}/{} \\\n-P {} -V {} -T {}\n'.format(self.library, self.libLibTyp, self.libPVTTyp[0], self.libPVTTyp[1], self.libPVTTyp[2])
        mmmcFile += 'create_op_cond -name op_wc\\\n -library_file {}/{} \\\n-P {} -V {} -T {}\n'.format(self.library, self.libLibMax, self.libPVTMax[0], self.libPVTMax[1], self.libPVTMax[2])
        mmmcFile += '### library_sets ###\n'
        mmmcFile += 'create_library_set -name NangateOpenCellLibrary_fast \\\n-timing {{{}/{}}}\n'.format(self.library, self.libLibMin)
        mmmcFile += 'create_library_set -name NangateOpenCellLibrary_slow \\\n-timing {{{}/{}}}\n'.format(self.library, self.libLibTyp)
        mmmcFile += 'create_library_set -name NangateOpenCellLibrary_typical \\\n-timing {{{}/{}}}\n'.format(self.library, self.libLibMax)
        mmmcFile += '### delay_corners ###\n'
        mmmcFile += 'create_delay_corner -name dc_bc -library_set \\\n {NangateOpenCellLibrary_fast} -opcond_library {fast} -opcond {op_bc} -rc_corner {rc_bc}\n'
        mmmcFile += 'create_delay_corner -name dc_wc -library_set \\\n {NangateOpenCellLibrary_slow} -opcond_library {slow} -opcond {op_wc} -rc_corner {rc_wc}\n'
        mmmcFile += 'create_delay_corner -name dc_tc -library_set \\\n {NangateOpenCellLibrary_typical} -opcond_library {typical} -opcond {op_tc} -rc_corner {rc_tc}\n'

        return mmmcFile

    def process(self, root='.'):
        message = ''
        update = {}

        # message += 'Creating MMMC file...\n'
        # with open(self.PAR_MMMC_FILE, 'r') as f:
        #     mmmc_list = [x[:-1] for x in f.readlines() if len(x) > 1]
        # mmmc_list.insert(2, '# Generated based on {}, by par.py.'.format(self.PAR_MMMC_FILE))
        filename = self.mmmc
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'w')
        fp.write(''.join(self.createMMMC()))
        fp.write('create_constraint_mode -name {}_net -sdc_files {{{}/{}}}\n'.format(self.design, root, self.sdc))
        fp.write('create_analysis_view -name av_bc -constraint_mode {{{}_net}} -delay_corner {{dc_bc}}\n'.format(self.design))
        fp.write('create_analysis_view -name av_tc -constraint_mode {{{}_net}} -delay_corner {{dc_tc}}\n'.format(self.design))
        fp.write('create_analysis_view -name av_wc -constraint_mode {{{}_net}} -delay_corner {{dc_wc}}\n'.format(self.design))
        fp.write('set_analysis_view -setup {av_wc} -hold {av_bc}\n')
        message = message[:-1] + ' done!\n'
        fp.close()

        message += '\nCreating setup script...\n'
        filename = join(self.scripts, '01_setup.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')

        fp.write('set lib_path {}\n\n'.format(self.library))
        fp.write('set init_verilog ${}/{}\n'.format(rootHandle, self.netlist))
        fp.write('set init_mmmc_file ${}/{}\n'.format(rootHandle, self.mmmc))
        fp.write('set init_lef_file {{{}}}\n'.format(' '.join([self.library+ '/'+lef for lef in self.lef])))
        fp.write('set init_pwr_net {}\n'.format(self.pwr))
        fp.write('set init_gnd_net {}\n'.format(self.gnd))
        fp.write('set init_design_settop 0\n')
        fp.write('init_design\n')
        fp.write('fit\n')
        message = message[:-1] + ' done!\n'
        fp.close()

        message += 'Creating floorplan script...\n'
        filename = join(self.scripts, '02_floorplan.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('setIoFlowFlag 0\n')
        fp.write('floorPlan -coreMarginsBy die -site {} -r {} {} {}  {}  {}  {} \n'.format(self.site, self.aspectRatio, self.density, self.fromEdge, self.fromEdge, self.fromEdge, self.fromEdge))
        fp.write('fit\n')
        message = message[:-1] + ' done!\n'
        fp.close()

        message += 'Creating power ring placement script...\n'
        filename = join(self.scripts, '03_powerRings.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('setAddRingMode -stacked_via_top_layer {}\n'.format(self.topMetalLayer))
        fp.write('setAddRingMode -stacked_via_bottom_layer metal1\n')
        fp.write('addRing \\\n')
        fp.write('-skip_via_on_wire_shape Noshape \\\n')
        fp.write('-skip_via_on_pin Standardcell -center 1 \\\n')
        # fp.write('-stacked_via_top_layer {} \\\n'.format(self.topMetalLayer))
        fp.write('-type core_rings -jog_distance 0.095 -threshold 0.095 \\\n')
        fp.write('-nets {{{} {}}} \\\n'.format(self.gnd, self.pwr))
        # fp.write('-follow core -stacked_via_bottom_layer metal1 -layer {bottom metal1 top metal1 right metal2 left metal2} \\\n')
        fp.write('-follow core -layer {bottom metal1 top metal1 right metal2 left metal2} \\\n')
        fp.write('-width {} -spacing {} -offset {} -extend_corner {{bl br rb lb}}\n'.format(self.pwrRingWidth, self.pwrRingSpacing, self.pwrRingOffset))
        fp.write('# CASCADE: Power rings place. Consider placing power strips manually!\n')
        message = message[:-1] + ' done! (Consider placing power strips manually!)\n'
        fp.close()

        message += 'Creating power routing script...\n'
        filename = join(self.scripts, '04_routePower.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('sroute \\\n{ blockPin padPin padRing corePin floatingStripe } \\\n')
        fp.write('-layerChangeRange {{ metal1 {} }} \\\n'.format(self.topMetalLayer))
        fp.write('-blockPinTarget { nearestTarget } -padPinPortConnect { allPort oneGeom } \\\n')
        fp.write('-padPinTarget { nearestTarget } -corePinTarget { firstAfterRowEnd } \\\n')
        fp.write('-floatingStripeTarget { blockring padring ring stripe ringpin blockpin followpin } \\\n')
        fp.write('-allowJogging 1 -crossoverViaLayerRange {{ metal1 {} }} -nets {{ {} {} }} -allowLayerChange 1 \\\n'.format(self.topMetalLayer, self.gnd, self.pwr))
        fp.write('-blockPin useLef -targetViaLayerRange { metal1 metal10 }\n')
        fp.write('fit\n')
        message = message[:-1] + ' done!\n'
        fp.close()

        message += 'Creating cell placement script...\n'
        filename = join(self.scripts, '05_place.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('setDesignMode -process {}\n'.format(self.processNode))
        fp.write('setEndCapMode -reset\n')
        fp.write('setEndCapMode -boundary_tap false\n')
        fp.write('setPlaceMode -fp false\n')
        fp.write('setUsefulSkewMode -maxSkew True -noBoundary false -useCells {{ {} }} -maxAllowedDelay 1\n'.format(' '.join(self.libBuffers)))
        fp.write('setPlaceMode -reset\n')
        fp.write('setPlaceMode -congEffort auto -timingDriven 1 -modulePlan 1 -clkGateAware 0 -powerDriven 0 -ignoreScan 1 -reorderScan 1 -ignoreSpare 1 -placeIOPins 1 -moduleAwareSpare 0 -preserveRouting 0 -rmAffectedRouting 0 -checkRoute 0 -swapEEQ 0\n')
        fp.write('setPlaceMode -fp false\n')
        fp.write('placeDesign -inPlaceOpt\n')
        fp.write('setDrawView place\n')
        fp.write('setOptMode -fixCap true -fixTran true -fixFanoutLoad false\n')
        fp.write('optDesign -preCTS\n')
        fp.write('getFillerMode -quiet\n')
        fp.write('checkPlace\n')
        fp.write('fit\n')
        message = message[:-1] + ' done! (Consider modifying the setUsefulSkewMode command.)\n'
        fp.close()

        if self.clk:
            message += 'Creating CTS script...\n'
            filename = join(self.scripts, '06_cts.tcl')
            rootHandle = self.createTclScript(filename, root)
            fp = open(filename, 'a')
            message = message[:-1] + ' done!\n'
            fp.close()
        else:
            message += 'No clock found in the design. Skipping CTS script generation.\n'

        message += 'Creating cell routing script...\n'
        filename = join(self.scripts, '07_route.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('setDesignMode -process {}\n'.format(self.processNode))
        fp.write('setNanoRouteMode -quiet -drouteStartIteration default\n')
        fp.write('setNanoRouteMode -quiet -routeTopRoutingLayer default\n')
        fp.write('setNanoRouteMode -quiet -routeBottomRoutingLayer default\n')
        fp.write('setNanoRouteMode -quiet -drouteEndIteration default\n')
        fp.write('setNanoRouteMode -quiet -routeWithTimingDriven true\n')
        fp.write('setNanoRouteMode -quiet -routeWithSiDriven false\n')
        fp.write('routeDesign -globalDetail\n')
        fp.write('verifyConnectivity -type all -error 1000 -warning 50\n')
        fp.write('setVerifyGeometryMode -area { 0 0 0 0 } -minWidth true -minSpacing true -minArea true -sameNet true -short true -overlap true -offRGrid false -offMGrid true -mergedMGridCheck true -minHole true -implantCheck true -minimumCut true -minStep true -viaEnclosure true -antenna false -insuffMetalOverlap true -pinInBlkg false -diffCellViol true -sameCellViol false -padFillerCellsOverlap true -routingBlkgPinOverlap true -routingCellBlkgOverlap true -regRoutingOnly false -stackedViasOnRegNet false -wireExt true -useNonDefaultSpacing false -maxWidth true -maxNonPrefLength -1 -error 1000\n')
        fp.write('verifyGeometry\n')
        fp.write('setVerifyGeometryMode -area { 0 0 0 0 }\n')
        message = message[:-1] + ' done!\n'
        fp.close()

        message += 'Creating cell placement script...\n'
        filename = join(self.scripts, '08_fill.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('getFillerMode -quiet\n')
        fp.write('addFiller -cell {} -prefix FILLER\n'.format(' '.join(self.libFillers)))
        fp.write('fit\n')
        message = message[:-1] + ' done! (Consider when to use this (before/after CTS, routing...)\n'
        fp.close()

        message += 'Creating output script...\n'
        filename = join(self.scripts, '09_report.tcl')
        rootHandle = self.createTclScript(filename, root)
        fp = open(filename, 'a')
        fp.write('set report_precision 6\n')
        fp.write('setExtractRCMode -engine {} -effortLevel {} -coupled {}\n'.format(self.setExtractRCMode_engine, self.setExtractRCMode_effortLevel, self.setExtractRCMode_coupled))
        fp.write('extractRC\n')
        fp.write('rcOut -rc_corner rc_wc -cUnit fF -setload par/max/{}.setload\n'.format(self.parSpef))
        fp.write('rcOut -rc_corner rc_wc -cUnit fF -setres par/max/{}.setres\n'.format(self.parSpef))
        fp.write('rcOut -rc_corner rc_wc -cUnit fF -spef par/max/{}\n'.format(self.parSpef))
        fp.write('update_timing\n')
        fp.write('set report_precision 3\n')
        fp.write('writeTimingCon {} -sdc\n'.format(self.parSdc))
        fp.write('write_sdf -version 2.1 {}\n'.format(self.parSdf))
        fp.write('saveNetlist {}\n'.format(self.parNetlist))
        fp.write('report_timing > {}\n'.format(self.parRpt))
        fp.write('fit\n')
        fp.write('#Generate GDS streamout manually.\n')
        message = message[:-1] + ' done! (Generate GDS streamout manually.)\n'
        fp.close()
        
        self.prepareFile(self.parNetlist)
        self.prepareFile(self.parSpef)
        self.prepareFile(self.parSdc)
        self.prepareFile(self.parSdf)


        return message, update