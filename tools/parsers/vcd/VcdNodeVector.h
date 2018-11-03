/* VcdNodeVector.h -- created by DS. */
#ifndef VcdNodeVector_H
#define VcdNodeVector_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "VcdNode.h"

// #define VCD_NODE_VECTOR_WORD_WIDTH      64
// #define VCD_NODE_VECTOR_WORD_TYPE       uint64_t
// #define VCD_NODE_VECTOR_WORD_FORMAT     "%016llx "
// #define VCD_NODE_VECTOR_STRTO_WORD      strtoull

#define VCD_NODE_VECTOR_WORD_WIDTH      32
#define VCD_NODE_VECTOR_WORD_TYPE       uint32_t
#define VCD_NODE_VECTOR_WORD_FORMAT     "%08x "
#define VCD_NODE_VECTOR_STRTO_WORD      strtoul

// #define VCD_NODE_VECTOR_WORD_WIDTH      16
// #define VCD_NODE_VECTOR_WORD_TYPE       uint16_t
// #define VCD_NODE_VECTOR_WORD_FORMAT     "%04x "
// #define VCD_NODE_VECTOR_STRTO_WORD      strtoul

#define VCD_NODE_VECTOR_WORD_N_BYTES    VCD_NODE_VECTOR_WORD_WIDTH / 8

typedef struct vcd_node_vector {
    uint16_t                            width;
    VCD_NODE_VECTOR_WORD_TYPE*          value;
    VcdNode**                           vcd_nodes;
    uint16_t                            _n_nodes;
    uint16_t                            _n_value_words;
    uint8_t                             _msw_pos;
} VcdNodeVector;

void 
VcdNodeVectorInit(
    VcdNodeVector*                      tgt, 
    uint16_t                            width
);

void
VcdNodeVectorBindNode(
    VcdNodeVector*                      tgt,
    VcdNode*                            node
);

void
VcdNodeVectorFinalize(
    VcdNodeVector*                      tgt,
    const char*                         name
);

void 
VcdNodeVectorKill(
    VcdNodeVector*                      tgt
);

void 
VcdNodeVectorToString(
    const VcdNodeVector*                tgt,
    const uint32_t                      indent                 
);

void
VcdNodeVectorEvaluate(
    VcdNodeVector*                      tgt
);

void
VcdNodeVectorSet(
    VcdNodeVector*                      tgt,
    const VCD_NODE_VECTOR_WORD_TYPE*    value
);

void
VcdNodeVectorGet(
    VcdNodeVector*                      tgt,
    VCD_NODE_VECTOR_WORD_TYPE*          dst
);

uint64_t
VcdNodeVectorEncode(
    const VcdNodeVector*                tgt,
    uint8_t*                            buff
);

uint64_t
VcdNodeVectorDecode(
    VcdNodeVector*                      tgt,
    const uint8_t*                      buff
);

uint64_t
VcdNodeVectorSize(
    const VcdNodeVector*                tgt
);

void
VcdNodeVectorFromString(
    VcdNodeVector*                      tgt,
    const char*                         str
);

uint8_t
VcdNodeVectorValueEq(
    VcdNodeVector*                      tgt1,
    VcdNodeVector*                      tgt2
);

#endif // VcdNodeVector_H
