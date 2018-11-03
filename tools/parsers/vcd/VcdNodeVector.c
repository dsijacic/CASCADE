/* VcdNodeVector.c -- created by DS. */
#include "VcdNodeVector.h"

void 
VcdNodeVectorInit(
    VcdNodeVector*                      tgt, 
    uint16_t                            width
) {
    uint64_t i;

    tgt->width = width; 
    tgt->_n_nodes = 0;
    // number of VCD_NODE_VECTOR_WORD_WIDTH-bit words, ceil(width/VCD_NODE_VECTOR_WORD_WIDTH)
    // position of the sigificant bit in the most sigificant is marked accordingly
    tgt->_n_value_words = width / VCD_NODE_VECTOR_WORD_WIDTH;
    if (width % VCD_NODE_VECTOR_WORD_WIDTH) {
        tgt->_msw_pos = width - VCD_NODE_VECTOR_WORD_WIDTH * tgt->_n_value_words;
        tgt->_n_value_words += 1;
    } else {
        tgt->_msw_pos = VCD_NODE_VECTOR_WORD_WIDTH;
    }
    // allocate and initialize value
    tgt->value = (VCD_NODE_VECTOR_WORD_TYPE*)malloc(tgt->_n_value_words * sizeof(VCD_NODE_VECTOR_WORD_TYPE));
    if (!tgt->value) {
        fprintf(stderr, "@VcdNodeVectorInit: malloc failed!\n");
        exit(-1);
    }
    for (i = 0; i < tgt->_n_value_words; i++)
        tgt->value[i] = 0;
    // allocate space for the node pointers, assume that all nodes are 1-bit,
    // hence the number of allocated pointers equals width
    tgt->vcd_nodes = (VcdNode**)malloc(tgt->width * sizeof(VcdNode*));
    if (!tgt->vcd_nodes) {
        fprintf(stderr, "@VcdNodeVectorInit: malloc failed!\n");
        exit(-1);
    }
    for (i = 0; i < tgt->width; i++)
        tgt->vcd_nodes[i] = 0;
}

void
VcdNodeVectorBindNode(
    VcdNodeVector*                      tgt,
    VcdNode*                            node
) {
    tgt->vcd_nodes[tgt->_n_nodes++] = node;
}

void
VcdNodeVectorFinalize(
    VcdNodeVector*                      tgt,
    const char*                         name
) {
    uint16_t total_width = 0;
    uint16_t i;
    // check if the total bit-width of nodes summs up to the desired width
    for (i = 0; i < tgt->_n_nodes; i++)
        total_width += tgt->vcd_nodes[i]->width;
    if (total_width != tgt->width) {
        fprintf(stderr, 
            "@VcdNodeVectorFinalize: Invalid combination of nodes for a %u-bit vector %s. Total width of its nodes is %u bits.\n", tgt->width, name, total_width);
        fprintf(stderr, 
            "@VcdNodeVectorFinalize: Check if the port map is correct.\n");
        for (i = 0; i < tgt->_n_nodes; i++) {
            fprintf(stderr, "\t%s [%u]\n", tgt->vcd_nodes[i]->name, tgt->vcd_nodes[i]->width);
        }
        exit(-1);
    }
    // trim allocated space in case multi-bit nodes exist
    if (tgt->_n_nodes < tgt->width) {
        tgt->vcd_nodes = (VcdNode**)realloc(tgt->vcd_nodes, tgt->_n_nodes * sizeof(VcdNode*));
        if (!tgt->vcd_nodes) {
            fprintf(stderr, "@VcdNodeVectorFinalize: realloc failed!\n");
            exit(-1);
        }
    }
    // notify user that the vector creation went well if name is not a 0 pointer
    if (name) {
        printf("Created %u-bit vector: %s\n", tgt->width, name);
    }
}

void 
VcdNodeVectorKill(
    VcdNodeVector*                      tgt
) {
    if (tgt->value)
        free(tgt->value);
    if (tgt->vcd_nodes)
        free(tgt->vcd_nodes);
    tgt->_n_nodes = 0;
}

void 
VcdNodeVectorToString(
    const VcdNodeVector*                tgt,
    const uint32_t                      indent                 
) {
    uint32_t i;
    for(i = 0; i < indent; i++) 
        printf("  ");
    for(i = 0; i < tgt->_n_value_words; i++)
        printf(VCD_NODE_VECTOR_WORD_FORMAT, tgt->value[i]);
    printf("[%u]\n", tgt->width);
}

void
VcdNodeVectorEvaluate(
    VcdNodeVector*                      tgt
) {

    uint64_t i, j, k, w;

    // initialize all value words to zero
    for(i = 0; i < tgt->_n_value_words; i++)
        tgt->value[i] = 0;

    // assuming all nodes are 1-bit ! 
    k = 0;
    j = 0;
    i = 0;
    // w = 0;

    // MSB word
    while (j < tgt->_msw_pos) { // 1 == vcd_nodes[i].width
        tgt->value[k] |= (VCD_NODE_VECTOR_WORD_TYPE)(tgt->vcd_nodes[i]->value[0]) << (VCD_NODE_VECTOR_WORD_TYPE)(tgt->_msw_pos - j - 1);
        j++;
        i++;
    }
    // Other words
    k++; 
    while(k < tgt->_n_value_words) {
        j = 0; // start from the word msb again
        while (j < VCD_NODE_VECTOR_WORD_WIDTH) {
            tgt->value[k] |= (VCD_NODE_VECTOR_WORD_TYPE)(tgt->vcd_nodes[i]->value[0]) << (VCD_NODE_VECTOR_WORD_TYPE)(VCD_NODE_VECTOR_WORD_WIDTH - j - 1);
            j++;
            i++;
        }
        k++;
    }
    // printf("(i = %llu) == (tgt->_n_nodes = %u): ", i, tgt->_n_nodes);
    // VcdNodeVectorToString(tgt, 0);
    
    // // assuming different bit widths 
    // k = 0;
    // j = 0;
    // i = 0;
    // w = 0;

    // // MSB word
    // // nodes that fully fit
    // while (j + tgt->vcd_nodes[i].width < tgt->_msw_pos) {
    //     for (w = 0; w < tgt->vcd_nodes[i].width; w++) {
    //         tgt->value[k] |= (VCD_NODE_VECTOR_WORD_TYPE)(tgt->vcd_nodes[i]->value[0]) << (VCD_NODE_VECTOR_WORD_TYPE)(tgt->_msw_pos - j - w - 1);
    //     }
    //     j += w;
    //     i++;
    // }
    // // node that overflows to the next word; if there is no overflow j == tgt->_msw_pos, and this is skipped entirely
    // while(j + w < tgt->_msw_pos) {
    //     tgt->value[k] |= (VCD_NODE_VECTOR_WORD_TYPE)(tgt->vcd_nodes[i]->value[0]) << (VCD_NODE_VECTOR_WORD_TYPE)(tgt->_msw_pos - j - w - 1);
    //     w++;
    // }
    // // Other words
    // k++; 
    // while(k < tgt->_n_value_words) {
    //     // start from the word msb again
    //     j = 0;
    //     // finish the overflown node from the last word if there is one
    //     while(w < tgt->vcd_nodes[i].width) {
    //         tgt->value[k] |= (VCD_NODE_VECTOR_WORD_TYPE)(tgt->vcd_nodes[i]->value[0]) << (VCD_NODE_VECTOR_WORD_TYPE)(VCD_NODE_VECTOR_WORD_WIDTH - j - 1);
    //     } 
    //     // move to the next node
    //     i++;

    //     while (j < VCD_NODE_VECTOR_WORD_WIDTH) {
    //         tgt->value[k] |= (VCD_NODE_VECTOR_WORD_TYPE)(tgt->vcd_nodes[i]->value[0]) << (VCD_NODE_VECTOR_WORD_TYPE)(VCD_NODE_VECTOR_WORD_WIDTH - j - 1);
    //         j++;
    //         i++;
    //     }
    //     k++;
    // }
}

void
VcdNodeVectorSet(
    VcdNodeVector*                      tgt,
    const VCD_NODE_VECTOR_WORD_TYPE*    src
) {
    uint64_t i;
    for (i = 0; i < tgt->_n_value_words; i++) {
        tgt->value[i] = src[i];
    }
}

void
VcdNodeVectorGet(
    VcdNodeVector*                      tgt,
    VCD_NODE_VECTOR_WORD_TYPE*          dst
) {
    uint64_t i;
    for (i = 0; i < tgt->_n_value_words; i++) {
        dst[i] = tgt->value[i];
    }
}

// I/O encoding
uint64_t
VcdNodeVectorEncode(
    const VcdNodeVector*                tgt,
    uint8_t*                            buff
) {
    uint32_t i, j, pos;

    pos = 0;
    for (i = 0; i < tgt->_n_value_words; i++) {
        for (j = 0; j < VCD_NODE_VECTOR_WORD_N_BYTES; j++) {
            buff[pos++] = (tgt->value[i] >> (j * 8) ) & 0xff;    
        }
        // buff[pos++] = (tgt->value[i]      ) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 8 ) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 16) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 24) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 32) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 40) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 48) & 0xff;
        // buff[pos++] = (tgt->value[i] >> 54) & 0xff;
    }
    return pos;
}

uint64_t
VcdNodeVectorDecode(
    VcdNodeVector*                      tgt,
    const uint8_t*                      buff
) {
    uint32_t i, j, pos;

    pos = 0;
    for (i = 0; i < tgt->_n_value_words; i++) {
        tgt->value[i] = 0;
        for (j = 0; j < VCD_NODE_VECTOR_WORD_N_BYTES; j++) {
            tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << (j * 8) ;
        }
        // tgt->value[i]  = (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++]      ;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 8 ;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 16;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 24;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 32;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 40;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 48;
        // tgt->value[i] += (VCD_NODE_VECTOR_WORD_TYPE)buff[pos++] << 54;
    }
    return pos;
}

// encoded size of the vector
uint64_t
VcdNodeVectorSize(
    const VcdNodeVector*                tgt
) {
    return VCD_NODE_VECTOR_WORD_N_BYTES * tgt->_n_value_words;
}

void
VcdNodeVectorFromString(
    VcdNodeVector*                      tgt,
    const char*                         str
) {
    char buffer[VCD_NODE_VECTOR_WORD_WIDTH+1];
    uint32_t msw_pos;
    uint32_t words_in_string;
    uint32_t i;

    switch(str[0]) {
    case 'b':
        // check data width
        if (tgt->width < strlen(&str[1])) 
            fprintf(stderr, 
            "@VcdNodeVectorFromString: String accomodates %u-bit values, ignoring %u highest bits of the input value %s.\n", strlen(&str[1]), strlen(&str[1]) - tgt->width, str);
        // Start reading the binary
        words_in_string = strlen(&str[1]) % VCD_NODE_VECTOR_WORD_WIDTH ? strlen(&str[1]) / VCD_NODE_VECTOR_WORD_WIDTH + 1 : strlen(&str[1]) / VCD_NODE_VECTOR_WORD_WIDTH;
        msw_pos = strlen(&str[1]) % VCD_NODE_VECTOR_WORD_WIDTH ? strlen(&str[1]) - (words_in_string - 1) * VCD_NODE_VECTOR_WORD_WIDTH: VCD_NODE_VECTOR_WORD_WIDTH;
        for (i = words_in_string - 1; i > 0; i--) {
            snprintf(buffer, VCD_NODE_VECTOR_WORD_WIDTH+1, "%s", &str[1 + msw_pos + (i-1) * VCD_NODE_VECTOR_WORD_WIDTH]);
            // printf("%u [%lu] %s\n", i, strlen(buffer), buffer);
            tgt->value[tgt->_n_value_words - words_in_string + i] = VCD_NODE_VECTOR_STRTO_WORD(buffer, 0, 2);
        }
        snprintf(buffer, msw_pos+1, "%s", &str[1]);
        // printf("%u [%lu] %s\n", i, strlen(buffer), buffer);
        tgt->value[tgt->_n_value_words - words_in_string + i] = VCD_NODE_VECTOR_STRTO_WORD(buffer, 0, 2);
        break;
    case 'x':
        // check data width
        if (tgt->width < strlen(&str[1]) * 4) 
            fprintf(stderr, 
            "@VcdNodeVectorFromString: String accomodates %u-bit values, ignoring %u highest bits of the input value %s.\n", strlen(&str[1]) * 4, strlen(&str[1]) * 4 - tgt->width, str);
        // Start reading the binary
        words_in_string = strlen(&str[1]) % (VCD_NODE_VECTOR_WORD_WIDTH / 4) ? strlen(&str[1]) / (VCD_NODE_VECTOR_WORD_WIDTH / 4) + 1 : strlen(&str[1]) / (VCD_NODE_VECTOR_WORD_WIDTH / 4);
        msw_pos = strlen(&str[1]) % (VCD_NODE_VECTOR_WORD_WIDTH / 4) ? strlen(&str[1]) - (words_in_string - 1) * (VCD_NODE_VECTOR_WORD_WIDTH / 4): (VCD_NODE_VECTOR_WORD_WIDTH / 4);
        for (i = words_in_string - 1; i > 0; i--) {
            snprintf(buffer, (VCD_NODE_VECTOR_WORD_WIDTH / 4)+1, "%s", &str[1 + msw_pos + (i-1) * (VCD_NODE_VECTOR_WORD_WIDTH / 4)]);
            // printf("%u [%lu] %s\n", i, strlen(buffer), buffer);
            tgt->value[tgt->_n_value_words - words_in_string + i] = VCD_NODE_VECTOR_STRTO_WORD(buffer, 0, 16);
        }
        snprintf(buffer, msw_pos+1, "%s", &str[1]);
        // printf("%u [%lu] %s\n", i, strlen(buffer), buffer);
        tgt->value[tgt->_n_value_words - words_in_string + i] = VCD_NODE_VECTOR_STRTO_WORD(buffer, 0, 16);
        break;
    default:
        fprintf(stderr, "@VcdNodeVectorFromString: Invalid value string %s\n", str);
        exit(-1);
        break;
    }
}

uint8_t
VcdNodeVectorValueEq(
    VcdNodeVector*                      tgt1,
    VcdNodeVector*                      tgt2
) {
    uint16_t i;
    for (i = 0; i < tgt1->_n_value_words; i++) {
        if (tgt1->value[i] !=  tgt2->value[i]) {
            return 0;
        }
    }
    return 1;
}

// void
// VcdNodeVectorUnmask(
//     VcdNodeVector*                      src, 
//     VcdNodeVector*                      dst, 
//     uint32_t                            n_shares
// ) {
//     node_value_t* src_values = (node_value_t*)malloc(src->width * sizeof(node_value_t));
//     if (!src_values) {
//         fprintf(stderr, "@VcdNodeVectorUnmask: malloc failed.\n", str);
//         exit(-1);
//     }
//     uint32_t i = 0;
//     while (i < src->_msw_pos) {
        
//     }
//     free(src_values);
// }