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
#> File name     : fix2allgen.py                                                
#> Time created  : Wed May 16 15:41:41 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from generators.lsimgen import LogicSimGenerator

class Fix2AllGen(LogicSimGenerator):

    def __init__(self):
        super(Fix2AllGen, self).__init__('f2all')

    def getData(self, nBits, initValue, nFrames):
        if nBits > 32 and nFrames == 2**32 - 1:
            print('Warning: This might be too much.')
            print('Warning: Try batching.')

        nBytes = nBits // 8
        if nBits % 8: nBytes += 1

        data = [0] * (2 * 2**nBits)
        for i in range(0, 2* 2**nBits, 2):
            data[i] = initValue
            data[i+1] = i >> 1

        return data, nBytes


