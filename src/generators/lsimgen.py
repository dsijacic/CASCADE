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
#> File name     : lsimgen.py                                                   
#> Time created  : Fri Apr  6 15:20:34 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from generator import Generator, GeneratorError
from os.path import isfile
import re

class LogicSimGenerator(Generator):

    """ Generator for logical simulations. Uses QuestaSim. """

    def generate(self, nBits, nFrames, batchSize, fileName, initValue=0):

        if batchSize:
            """ start batching """
            raise NotImplementedError('Not yet implemented.')
        else:
            """ no batching, single file """

            frameTransitions, nBytes = self.getData(nBits, initValue, nFrames)

            fp = open(fileName, 'wb')
            mask = 2**nBits - 1
            for tran in frameTransitions:
                tran &= mask
                fp.write(tran.to_bytes(nBytes, byteorder='big'))
            fp.close()

    def getData(self, nBits, initValue, nFrames):
        raise NotImplementedError('Virtual class.')

