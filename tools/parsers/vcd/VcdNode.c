/* VcdNode.c -- created by DS. */
#include "VcdNode.h"

vcd_id_t VcdNodeCreate(VcdNode** collection, CHAR* vcd_header_line, CHAR* name_prefix, CHAR hier_separator) 
{
    /* vcd_header_line := $var {wire|reg} <width> <id> <name> [<bus_addr>] */

    CHAR* split;

    UI64 width; 
    node_type_t type;

    vcd_id_t id;
    UI64 basis;
    UI64 i;
    // fprintf(stderr, "%s\n", vcd_header_line);

    // $var
    split = strtok(vcd_header_line, " \n");
    if (strcmp(split, "$var")) {
        type = REG;
        fprintf(stderr, "@VcdNodeCreate: Invalid line %s.\n", vcd_header_line);
        exit (-1);
    } 
    // {wire| reg}
    split = strtok(0, " \n");
    if (0 == strcmp(split, "wire")) {
        type = WIRE;
    } else
    if (0 == strcmp(split, "reg")) {
        type = REG;
        // fprintf(stderr, "@VcdNodeCreate: Verilog register (reg) not supported.\n");
        // exit (-1);
    } else {
        fprintf(stderr, "@VcdNodeCreate: Invalid type %s, or invalid $var line %s.\n", split, vcd_header_line);
        exit (-1);
    }
    // <width>
    split = strtok(0, " \n");
    width = atoi(split);
    if (width != 1) {
        fprintf(stderr, "@VcdNodeCreate: Only nodes with width 1 are supported!.\n");
        fprintf(stderr, "@VcdNodeCreate: Line %s cannot be parsed!\n", vcd_header_line);
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
    (*collection)[id].name = (CHAR*)malloc(strlen(name_prefix) + 1 + strlen(split) + 1);
    if (!(*collection)[id].name) {
        fprintf(stderr, "@VcdNodeCreate: name malloc failed!");
        exit(-1);
    }
    sprintf((*collection)[id].name, "%s%c%s", name_prefix, hier_separator, split);
    // [<bus>]
    split = strtok(0, " \n");
    if (0 != strcmp(split, "$end")) {
        (*collection)[id].name = (CHAR*)realloc((*collection)[id].name, strlen((*collection)[id].name) + strlen(split) + 1);
        if (!(*collection)[id].name) {
            fprintf(stderr, "@VcdNodeCreate: name realloc failed!");
            exit(-1);
        }
        sprintf((*collection)[id].name, "%s%s", (*collection)[id].name, split);
    }
    // $end
    (*collection)[id].width = width;
    (*collection)[id].type = type;
    (*collection)[id].value = (node_value_t*)malloc(width * sizeof(node_value_t));
    if (!(*collection)[id].value) {
        fprintf(stderr, "@VcdNodeCreate: value malloc failed!");
        exit(-1);
    }
    for (i = 0; i < width; i++)
        (*collection)[id].value[i] = X;

    return id;
}

// Removes the entire collection of nodes, add signle node removal if it starts
// making sense at some point.
void VcdNodeRemove(VcdNode** collection, UI64 collection_size) 
{
    UI64 i;
    for (i = 0; i < collection_size; i++) {
        if ((*collection)[i].name) 
            free((*collection)[i].name); 
        if ((*collection)[i].value) 
            free((*collection)[i].value); 
    }
    free(*collection);
}

void VcdNodeShowCollection(VcdNode** collection, UI64 collection_size)
{
    UI64 i;
    for (i = 0; i < collection_size; i++) {
        fprintf(stdout, "id = %llu -> w = %u val = %02x name = %s\n", i, 
            (*collection)[i].width, 
            *(*collection)[i].value, 
            (*collection)[i].name);
    }
}

// Initialize to whichever value there is in the VCD file.
void VcdNodeSetValue(VcdNode** collection, CHAR* vcd_body_line)
{
    vcd_id_t id;
    UI64 pos;
    UI64 basis;
    node_value_t value;

    pos = 1;
    if (vcd_body_line[0] == 'b') {
        vcd_body_line[0] = vcd_body_line[1];
        pos = 3;
    }
    switch (vcd_body_line[0]) {
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
        fprintf(stderr, "@VcdNodeSetValue: Unkown symbol %c found.\n", vcd_body_line[0]);
        exit(ERR_PARSING);
        break;
    }

    // pos = 1; // only the 1st character can be a value; 1-bit nodes!
    basis = 1;

    // compute id
    id = 0;
    while(vcd_body_line[pos] != '\n') {
        id += (vcd_body_line[pos++] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;
    // set value
    *(*collection)[id].value = value;

    // printf("%llu: %c -> %02x\n", id, vcd_body_line[0], *(*collection)[id].value);
}

// Update value from the VCD file, only 1 and 0 are permitted.
void VcdNodeUpdateValue(VcdNode** collection, CHAR* vcd_body_line) {

    vcd_id_t id;
    UI64 pos;
    UI64 basis;
    node_value_t value;

    pos = 1;
    if (vcd_body_line[0] == 'b') {
        vcd_body_line[0] = vcd_body_line[1];
        pos = 3;
    }
    switch (vcd_body_line[0]) {
    case '1':
        value = H;
        break;
    case '0':
        value = L;
        break;
    default:
        fprintf(stderr, "@VcdNodeUpdateValue: Invalid value %c found.\n", vcd_body_line[0]);
        exit(-1);
        break;
    }

    // pos = 1; // only the 1st CHARacter can be a value; 1-bit nodes!
    basis = 1;

    // compute id
    id = 0;
    while(vcd_body_line[pos] != '\n') {
        id += (vcd_body_line[pos++] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;
    // set value
    *(*collection)[id].value = value;

    // printf("%llu: %c -> %02x\n", id, vcd_body_line[0], *(*collection)[id].value);
}

node_value_t VcdNodeGetBit(VcdNode* tgt) {
    return tgt->value[0];
}

// Parses a VCD body line and updates the value of the node.
// Returns a power contribution of the node transition, evaluated based on the
// power estimation function.
// TODO: Include all possible power models here.

// d_MSM
    // Every 0->1 toggle counts as 1.0
    // Every 1->0 toggle counts as 1.0 - d to account for assymetries
    // Nodes contained in the filter (filter points to them) are exluded (e.g., for
    // input nodes)
FL32 VcdNodeUpdate_d_MSM(
    VcdNode** collection, 
    CHAR* vcd_body_line, 
    FL32 d, 
    VcdNode** filter, 
    UI64 filter_size
)
{
    vcd_id_t id;
    UI64 pos;
    UI64 i;
    UI64 basis;
    node_value_t value;

    pos = 1;
    if (vcd_body_line[0] == 'b') {
        vcd_body_line[0] = vcd_body_line[1];
        pos = 3;
    }
    switch (vcd_body_line[0]) {
    case '1':
        value = H;
        break;
    case '0':
        value = L;
        break;
    default:
        fprintf(stderr, "@VcdNodeUpdate_d_MSM: Invalid value %s found.\n", vcd_body_line);
        exit(-1);
        break;
    }

    // pos = 1; // only the 1st CHARacter can be a value; 1-bit nodes!
    basis = 1;

    // compute id
    id = 0;
    while(vcd_body_line[pos] != '\n') {
        id += (vcd_body_line[pos++] - '!' + 1) * basis;
        basis *= '~' - ' ';
    }
    id--;

    // evaluate power if this node is not supposed to be filtered out
    for (i = 0; i < filter_size; i++) {
        if (filter[i] == &((*collection)[id])) {
            *(*collection)[id].value = value;
            return 0.0;
        }
    }

    // printf("value = %02x, *(*collection)[id].value = %02x\n", value, *(*collection)[id].value);
    if (value > *(*collection)[id].value) {
        *(*collection)[id].value = value;
        return 1.0;
    } else 
    if (value < *(*collection)[id].value) {
        *(*collection)[id].value = value;
        return 1.0 - d;
    } else
    {
        return 0.0;
    }

}

