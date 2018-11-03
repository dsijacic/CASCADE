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
// File name     : vcdvector.h                                                  
// Time created  : Mon Feb 12 10:26:39 2018                                     
// Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
// Details       :                                                              
//               :                                                              
// =============================================================================

#ifndef VCDVECTOR_H
#define VCDVECTOR_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <vcdnode.h>

typedef struct vcd_vector_t {
    uint64_t                    nbits;
    vcd_node**                  nodes;
    uint64_t                    _n_nodes;
    uint64_t                    _msw_pos;
    uint64_t                    _n_words;
} vcd_vector;

void
VcdVectorInit(
    vcd_vector*                 tgt,
    uint64_t                    nbits
) {
    tgt->nbits = nbits;
    tgt->_n_nodes = 0;
    tgt->_n_words = nbits / sizeof(uint64_t);
    if (nbits % sizeof(uint64_t)) {
        tgt->_msw_pos = nbits - sizeof(uint64_t) * tgt->_n_words;
        tgt->_n_words++;
    } else{
        tgt->_msw_pos = sizeof(uint64_t);
    }
    // allocate space for the node pointers, assume that all nodes are 1-bit,
    // hence the number of allocated pointers equals nbits
    // this is the worst case scenario
    tgt->nodes = (vcd_node**)malloc(tgt->nbits * sizeof(vcd_node*));
    if (!tgt->nodes) {
        fprintf(stderr, "@VcdVectorInit: malloc failed!\n");
        exit(-1);
    }
    for (i = 0; i < tgt->nbits; i++)
        tgt->nodes[i] = 0;
}

void
VcdVectorAppend(
    vcd_vector*                 tgt,
    vcd_node*                   node
) {
    tgt->nodes[tgt->_n_nodes++] = node;
}

void
VcdVectorFinalize(
    vcd_vector*                 tgt,
    const char*                 name
) {
    uint64_t total_nbits = 0;
    uint64_t i;
    // sanity check (length)
    for (i = 0; i < tgt->_n_nodes; i++)
        total_nbits += tgt->nodes[i]->nbits;
    if (total_nbits != tgt->nbits) {
        fprintf(stderr, 
            "Invalid combination of nodes for a %u-bit vector %s. \
            Total nbits of its nodes is %u bits.\n", 
            tgt->nbits, name, total_nbits);
        fprintf(stderr, 
            "Check if the port map is correct.");
        for (i = 0; i < tgt->_n_nodes; i++) {
            fprintf(stderr, "\t%s [%u]\n", tgt->nodes[i]->name, tgt->nodes[i]->nbits);
        }
        exit(-1);
    }
    // trim allocated space in case multi-bit nodes exist
    if (tgt->_n_nodes < tgt->nbits) {
        tgt->nodes = (VcdNode**)realloc(tgt->nodes, tgt->_n_nodes * sizeof(vcd_node*));
        if (!tgt->nodes) {
            fprintf(stderr, "@VcdVectorFinalize: realloc failed!\n");
            exit(-1);
        }
    }
    // notify user that the vector creation went well if name is not a 0 pointer
    if (name) {
        printf("Created %u-bit vector: %s\n", tgt->nbits, name);
    }
}

void
VcdVectorKill(
    vcd_vector*                 tgt
) {
    uint64_t i;
    if (tgt->nodes) {
        for (i = 0; i < tgt->_n_nodes; i++) {
            VcdNodeKill(tgt->nodes[i]);
            tgt->nodes[i] = 0;
        }
        free(tgt->nodes);
        tgt->nodes = 0;
    }
    tgt->_n_nodes = 0;
}

void
VcdVectorEvaluate(
    vcd_vector*                 tgt,
    uint64_t**                  value
) {
    uint64_t i, j, k;
    // uint64_t w;

    for (i = 0; i < tgt->_n_words; i++)
        (*value)[i] = 0;
    // assuming all nodes are 1-bit ! 
    k = 0;
    j = 0;
    i = 0;
    // w = 0;
    // MSB word
    while (j < tgt->_msw_pos) { // 1 == vcd_nodes[i].nbits
        (*value)[k] |= (uint64_t)(tgt->nodes[i]->value[0]) << (uint64_t)(tgt->_msw_pos - j - 1);
        j++;
        i++;
    }
    // other words
    k++;
    while (k < tgt->_n_words) {
        j = 0; 
        while(j < 64) {
            (*value)[k] |= (uint64_t)(tgt->vcd_nodes[i]->value[0]) << (uint64_t)(64 - j - 1);
            j++;
            i++;
        }
        k++;
    }
}

#endif // VCDVECTOR_H
