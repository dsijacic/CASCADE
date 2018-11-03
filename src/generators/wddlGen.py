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
#> File name     : wddlGen.py                                                   
#> Time created  : Mon Oct  8 11:07:14 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from generators.lsimgen import LogicSimGenerator
from generator import GeneratorError
from tqdm import tqdm

class WddlGen(LogicSimGenerator):

    def __init__(self):
        super(WddlGen, self).__init__('wddl')

    def getData(self, nBits, initValue, nFrames):


        if nBits % 2:
            raise GeneratorError('WDDL circuits must have an even number of bits!')

        self.dataBits = nBits // 2

        nBytes = nBits // 8
        if nBits % 8: nBytes += 1

        data = []
        data.append(self.precharge())
        data.append(self.evaluate(initValue))

        for i in range(initValue, initValue + nFrames):
            data.append(self.precharge())
            data.append(self.evaluate(i))

        data.append(self.precharge())

        return data, nBytes

    def precharge(self, pcValue=0):
        """ precharge to all zeros or all ones """
        return pcValue * (2**(self.dataBits * 2) -1)

    def evaluate(self, data):
        """ evaluation phase """
        return data << self.dataBits | ~data & (2**self.dataBits - 1)
