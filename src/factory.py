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
#> File name     : factory.py                                                   
#> Time created  : Sat Mar 24 16:41:58 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================


from generators                 import *
from handlers                   import *

class FactoryError(Exception):
    """..."""

class Factory():

    allHandlers = []

    def create(cli):
        Factory.allHandlers.append(TestbenchGenerator(
                EDPCGen(), 
                DevRandGen(), 
                DevURandGen(),
                Fix2AllGen(),
                WddlGen(),
        ))
        Factory.allHandlers.append(DcShell())
        Factory.allHandlers.append(Innovus())
        Factory.allHandlers.append(QuestaSim())
        Factory.allHandlers.append(PrimeTime())
        Factory.allHandlers.append(Vcd2Pff())
        for h in Factory.allHandlers:
            cli.addCommand(h.handle, h.help, h.args)

    def get(handle):
        for h in Factory.allHandlers:
            if handle == h.handle:
                return h
        raise FactoryError('Factory received an unkown handle "{}".'.format(handle))
