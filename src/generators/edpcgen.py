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
#> File name     : edpcgen.py                                                   
#> Time created  : Sat Mar 24 11:43:37 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from generators.lsimgen import LogicSimGenerator

class EDPCGen(LogicSimGenerator):

    def __init__(self):
        super(EDPCGen, self).__init__('edpc')

    def getData(self, nBits, initValue, nFrames):

        """ In this case initValue is the index in the EDPC sequence. """

        if nBits > 12 and 2**(2*nBits) - 2**nBits == nFrames:
            print('Warning: Generating EDPC sequence for {} input bits. This might take a while.'.format(nBits))
            print('Warning: Try batching.')

        nBytes = nBits // 8
        if nBits % 8: nBytes += 1

        self.init = 1
        self.jump = 1
        self.node = 0

        self.space = 1 << nBits
        self.total = (1 << (2 * nBits)) - (1 << nBits)

        data = [0] * (nFrames + 1)

        i = 0
        while i < initValue:
            data[0] = self.clockEdpc()
            i += 1
        i = 0
        while i < nFrames:
            data[i+1] = self.clockEdpc()
            i += 1

        return data, nBytes

    def clockEdpc(self):
        self.node = (self.node + self.jump) % self.space
        self.jump = (1         + self.jump) % self.space
        if self.node == 0:
            self.init = (self.init + 1)  % self.space
            self.jump = self.init
        if self.jump == 0:
            self.jump = 1
        return self.node



