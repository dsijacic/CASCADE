/* defs.h -- created by DS. */
// =============================================================================
//                     This confidential and proprietary code                   
//                       may be used only as authorized by a                    
//                         licensing agreement from                             
//                     KU Leuven, ESAT Department, COSIC Group                  
//                    https://securewww.esat.kuleuven.be/cosic/                 
//                        _____  ____    ____   ____  _____                     
//                       / ___/ / __ \  / __/  /  _/ / ___/                     
//                      / /__  / /_/ / _\ \   _/ /  / /__                       
//                      \___/  \____/ /___/  /___/  \___/                       
//                                                                              
//                              ALL RIGHTS RESERVED                             
//        The entire notice above must be reproduced on all authorized copies.  
// =============================================================================
// File name     : defs.h                                                      
// Time created  : Thu Nov 16 13:46:19 2017                                     
// Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
// Details       :                                                              
//               :                                                              
// =============================================================================

#ifndef defs_H
#define defs_H

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef unsigned char           ERR_CODE;
#define ERR_SUCCESS             0x00
#define ERR_GENERAL             0x01
#define ERR_MALLOC              0x02
#define ERR_REALLOC             0x03
#define ERR_DIVBYZERO           0x04
#define ERR_INVALID_WAVEFORM    0x05
#define ERR_IO                  0x06
#define ERR_STR                 0x07
#define ERR_EXCESS              0x08
#define ERR_SET                 0x09
#define ERR_PARSING             0x0a
#define ERR_VALUE               0x0b
#define ERR_MISS                0x0c
#define ERR_ARGS                0xff

typedef int8_t                  SI08;
typedef uint8_t                 UI08;
typedef int16_t                 SI16;
typedef uint16_t                UI16;
typedef uint32_t                UI32;
typedef uint64_t                UI64;
typedef int32_t                 SI32;
typedef int64_t                 SI64;
typedef float                   FL32;
typedef double                  FL64;
typedef char                    CHAR;
typedef uint8_t                 BYTE;
typedef uint8_t                 FLAG;

typedef enum enum_wave {
    MSM = 0,
    REC = 1
} WaveEnum;

typedef enum enum_partition {
    F = 0,
    R = 1
} PART;

typedef enum enum_target {
    FI = 0,
    FO = 1
} FIFO;

#define READ_LINE_SIZE                  (1 << 12)
#define MAX_LINE_SIZE                   (1 << 12)
#define FRAME_MIN_ALLOC_EVENTS          (1 << 15)

#define RW_BUFFER_SIZE                  ((1 << 30) + (1 << 29))

#endif //
