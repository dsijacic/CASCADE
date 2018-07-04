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
#> File name     : utils.py                                                     
#> Time created  : Tue Jun 26 10:10:12 2018                                     
#> Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
#> Details       :                                                              
#>               :                                                              
#> =============================================================================

def ppDict(d, l=0):
    pp = ''
    assert type(d) == dict
    for k, v in d.items():
        pp += '|' + l * '--' + '> ' + str(k)
        if type(v) == dict:
            pp += '\n'
            pp += ppDict(v, l + 1)
        else:
            pp += ': ' + str(v) + '\n'
    return pp