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
#> File name     : generator.py                                                 
#> Time created  : Fri Mar 23 15:32:27 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

from struct                 import pack, unpack
from generators             import *

class GeneratorError(Exception):
    ...

class Generator(object):

    def wrUI08(fp, value): fp.write(pack('>B', value))
    def wrUI16(fp, value): fp.write(pack('>H', value))
    def wrUI32(fp, value): fp.write(pack('>I', value))
    def wrUI64(fp, value): fp.write(pack('>Q', value))

    def rdUI08(fp):        fp.unpack('>B', fp.read(1))
    def rdUI16(fp):        fp.unpack('>H', fp.read(2))
    def rdUI32(fp):        fp.unpack('>I', fp.read(4))
    def rdUI64(fp):        fp.unpack('>Q', fp.read(8))
    
    def __init__(self, handle):
        self.handle = handle

    def generate(self, *args):
        raise NotImplementedError('Specify the generator!')
