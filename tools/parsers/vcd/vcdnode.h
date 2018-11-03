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
// File name     : vcdnode.h                                                    
// Time created  : Mon Feb 12 10:26:34 2018                                     
// Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
// Details       :                                                              
//               :                                                              
// =============================================================================

#ifndef VCDNODE_H
#define VCDNODE_H

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

typedef enum logic_t {
    X = 0xff,
    U = 0xfe,
    Z = 0xfd,
    H = 0x01,
    L = 0x00
} logic;

typedef uint64_t                node_id;

typedef struct vcd_node_t {
    char*                       name;
    uint16_t                    width;
    uint8_t                     include;
    logic*                      value;
} vcd_node;

node_id VcdNodeCreate(
    vcd_node**                  collection, 
    uint64_t*                   line_number,
    char*                       vcd_header_line, 
    char*                       name_prefix,
    char                        hier_separator
) {
    /* vcd_header_line := $var {wire|reg} <width> <id> <name> [<bus_addr>] */
    char* split;
    uint16_t width;
    uint64_t basis;
    uint64_t i;
    node_id id;
    // $var
    split = strtok(vcd_header_line, " \n");
    // {wire|reg}
    split = strtok(0, " \n");
    // <width>
    split = strtok(0, " \n");
    width = atoi(split);
    if (width != 1) {
        fprintf(stderr, "Found a vector node at line %u. Can not be parsed!\n", *line_number);
        exit(-1);
    }
    // <id>
    split = strtok(0, " \n");
    id = 0;
    basis = 1;
    for (i = 0; i < strlen(split); i++) {
        id += (split[i] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;
    // <name> = <name_prefix>/<name>[<bus>]
    split = strtok(0, " \n");
    (*collection)[id].name = (char*)malloc(strlen(name_prefix) + 1 + strlen(split) + 1);
    if (!(*collection)[id].name) {
        fprintf(stderr, "@VcdNodeCreate: name malloc failed!");
        exit(-1);
    }
    sprintf((*collection)[id].name, "%s%c%s", name_prefix, hier_separator, split);
    // [<bus>]
    split = strtok(0, " \n");
    if (0 != strcmp(split, "$end")) {
        (*collection)[id].name = (char*)realloc((*collection)[id].name, strlen((*collection)[id].name) + strlen(split) + 1);
        if (!(*collection)[id].name) {
            fprintf(stderr, "@VcdNodeCreate: name realloc failed!");
            exit(-1);
        }
        sprintf((*collection)[id].name, "%s%s", (*collection)[id].name, split);
    }
    // $end
    (*collection)[id].width = width;
    (*collection)[id].include = 1;
    (*collection)[id].value = (logic*)malloc(width* sizeof(logic));
    if (!(*collection)[id].value) {
        fprintf(stderr, "@VcdNodeCreate: value malloc failed!");
        exit(-1);
    }
    for (i = 0; i < width; i++)
        (*collection)[id].value[i] = X;
    (*line_number)++;
    return id;
}

void VcdNodeSet(
    vcd_node**                  collection, 
    uint64_t*                   line_number,
    char*                       vcd_line
) {
    node_id                     id;
    uint64_t                    pos;
    uint64_t                    basis;
    logic                       value;

    // hardcoded register parsing for single bit registers
    pos = 1;
    if (vcd_line[0] == 'b') {
        vcd_line[0] = vcd_line[1];
        pos = 3;
    }
    switch (vcd_line[0]) {
    case '1':
        value = H;
        break;
    case '0':
        value = L;
        break;
    case 'X':
    case 'x':
        value = X;
        break;
    case 'Z':
    case 'z':
        value = Z;
        break;
    case 'U':
    case 'u':
        value = U;
        break;
    default:
        fprintf(stderr, "Unkown symbol %c found in line %u.\n", vcd_line[0], *line_number);
        exit(-1);
        break;
    }
    // pos = 1; // only the 1st character can be a value; 1-bit nodes!
    basis = 1;
    // compute id
    id = 0;
    while(vcd_line[pos] != '\n') {
        id += (vcd_line[pos++] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;
    // set value
    *(*collection)[id].value = value;
}

void VcdNodeUpdate(
    vcd_node**                  collection, 
    uint64_t*                   line_number,
    char*                       vcd_line
) {
    node_id                     id;
    uint64_t                    pos;
    uint64_t                    basis;
    logic                       value;

    // hardcoded register parsing for single bit registers
    pos = 1;
    if (vcd_line[0] == 'b') {
        vcd_line[0] = vcd_line[1];
        pos = 3;
    }
    switch (vcd_line[0]) {
    case '1':
        value = H;
        break;
    case '0':
        value = L;
        break;
    default:
        fprintf(stderr, "Invalid value %c found in line %u.\n", vcd_line[0], *line_number);
        exit(-1);
        break;
    }
    // pos = 1; // only the 1st character can be a value; 1-bit nodes!
    basis = 1;
    // compute id
    id = 0;
    while(vcd_line[pos] != '\n') {
        id += (vcd_line[pos++] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;
    // set value
    *(*collection)[id].value = value;
}

void VcdNodeUpdateAndCount(
    vcd_node**                  collection,
    uint64_t*                   line_number,
    char*                       vcd_line,
    uint64_t*                   n_rise,
    uint64_t*                   n_fall
) {
    node_id                     id;
    uint64_t                    pos;
    uint64_t                    i;
    uint64_t                    basis;
    logic                       value;

    pos = 1;
    if (vcd_line[0] == 'b') {
        vcd_line[0] = vcd_line[1];
        pos = 3;
    }
    switch (vcd_line[0]) {
    case '1':
        value = H;
        break;
    case '0':
        value = L;
        break;
    default:
        fprintf(stderr, "Invalid value %c found in line %u.\n", vcd_line[0], *line_number);
        exit(-1);
        break;
    }
    // pos = 1; // only the 1st character can be a value; 1-bit nodes!
    basis = 1;
    // compute id
    id = 0;
    while(vcd_line[pos] != '\n') {
        id += (vcd_line[pos++] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;
    // toggle count
    if ((*collection)[id].include) {
        // rising edge
        if (value > *(*collection)[id].value)
            (*n_rise)++;
        // falling edge
        else if (value < *(*collection)[id].value)
            (*n_fall)++;
        // assign new value
        *(*collection)[id].value = value;
    }
}

void
VcdNodeKill(
    vcd_node*                   tgt
) {
    if (tgt->name)
        free (tgt->name);
    if (tgt->value)
        free (tgt->value);
    tgt->width = 0;
    tgt->include = 0;
}
#endif // VCDNODE_H
