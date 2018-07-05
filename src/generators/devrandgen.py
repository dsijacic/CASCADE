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
#> File name     : devrandgen.py                                                
#> Time created  : Sat Mar 24 11:59:39 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from generators.lsimgen import LogicSimGenerator

class DevRandGen(LogicSimGenerator):

    def __init__(self):
        super(DevRandGen, self).__init__('devr')

    def getData(self, nBits, initValue, nFrames):

        devr = open('/dev/random', 'rb')
        
        nbytes = nBits // 8
        if nBits % 8: nbytes += 1

        rawdata = devr.read(nbytes * (1 + nFrames))
        devr.close()

        data = [rawdata[x:x+nbytes] for x in range(0, len(rawdata), nbytes)]
        data = [int.from_bytes(d, byteorder='big') for d in data]

        return data, nbytes
