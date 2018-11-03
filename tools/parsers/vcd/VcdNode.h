/* VcdNode.h -- created by DS. */
#ifndef VcdNode_H
#define VcdNode_H

#include "defs.h"

// node values definition
typedef enum node_value {
    X = 0xff,
    U = 0xfe,
    Z = 0xfd,
    H = 0x01,
    L = 0x00
} node_value_t;

typedef UI64 vcd_id_t;

// ... aditional contextual information (e.g., power H->L)
typedef enum node_type {
    WIRE, 
    REG
} node_type_t;

// node structure, general case is given here
// this approach gives better perforamance for nodes with width 1,
// still it is not hardcoded for easier addoption if multi-bit nodes are
// ever needed; 
typedef struct vcd_node {
    char*                               name;  // corresponding name in the hier
    uint16_t                            width; // will be fixed to 1 for now
    node_type_t                         type;  // wire or reg
    node_value_t*                       value; // width-element array 
} VcdNode;

// Nodes are created from VCD headers.
// They are stored in an array of nodes, and their ID is encoded to the address
// in this array.
vcd_id_t VcdNodeCreate(VcdNode** collection, char* vcd_header_line, char* name_prefix, char hier_separator);

// Removes the entire collection of nodes, add signle node removal if it starts
// making sense at some point.
void VcdNodeRemove(VcdNode** collection, UI64 collection_size);
// For debugging only
void VcdNodeShowCollection(VcdNode** collection, UI64 collection_size);

// Initialize to whichever value there is in the VCD file.
void VcdNodeSetValue(VcdNode** collection, char* vcd_body_line);

// Update value from the VCD file, only 1 and 0 are permitted.
void VcdNodeUpdateValue(VcdNode** collection, char* vcd_body_line);

// Parses a VCD body line and updates the value of the node.
// Returns a power contribution of the node transition, evaluated based on the
// power estimation function.
// TODO: Include all possible power models here.
FL32 VcdNodeUpdate_d_MSM(VcdNode** collection, char* vcd_body_line, FL32 d, VcdNode** filter, UI64 filter_size);

// Returns the value of the 1 bit wide nodes
node_value_t VcdNodeGetBit(VcdNode* tgt);
#endif //
