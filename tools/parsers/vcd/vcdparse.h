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
// File name     : vcdparse.h                                                   
// Time created  : Mon Feb 12 15:07:08 2018                                     
// Author        : dsijacic (dsijacic@esat.kuleuven.be)                         
// Details       :                                                              
//               :                                                              
// =============================================================================

#ifndef VCDPARSE_H
#define VCDPARSE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../include/defs.h"
#include "vcdnode.h"

#define VCD_LINE_MAX        (1 << 10)

typedef struct vcd_file_t {
    char*                       file_name;
    FILE*                       vcdfp;
    vcd_node*                   nodes;
    uint64_t                    n_nodes;
    float                       timescale;
    char                        hier_separator;
    char                        line[VCD_LINE_MAX];
    char                        auxl[VCD_LINE_MAX];
    char*                       split;
    uint64_t                    line_cnt;
} vcd_file;

void
VcdOpen(
    vcd_file*                   self,
    char*                       file_name,
    char                        hier_separator
) {
    printf("VcdOpen\n");
    self->vcdfp = fopen(file_name, "r");
    if (!self->vcdfp) {
        fprintf(stderr, "File %s not found or inaccessible.\n", file_name);
        exit(-1);
    }
    self->file_name = (char*)malloc(strlen(file_name) + 1);
    if (!self->file_name) {
        fprintf(stderr, "malloc failed.\n");
        exit(-1);
    }
    strcpy(self->file_name, file_name);
    self->hier_separator = hier_separator;
    self->line_cnt = 0;
}

void
VcdClose(
    vcd_file*                   self
) {
    printf("VcdClose\n");
    if (self->file_name)        free(self->file_name);
    if (self->nodes)            free(self->nodes);
    if (self->vcdfp)            fclose(self->vcdfp);
}

void
VcdParseHeader(
    vcd_file*                   self
) {
    char                        scope[VCD_LINE_MAX] = {0};
    uint64_t                    scope_top;
    uint64_t                    scope_pos[256] = {0}; // allows 256 levels of hierarchy
    self->n_nodes = 0;
    // first run, count the nodes
    while (fgets(self->line, VCD_LINE_MAX, self->vcdfp)) {
        // end of header
        if (0 == strcmp(self->line, "$enddefinitions $end\n"))
            break;
        if (!strncmp(self->line, "$var", 4))
            self->n_nodes++;
        // timescale
        if (!strncmp(self->line, "$timescale", 10)) {
            fgets(self->line, VCD_LINE_MAX, self->vcdfp);
            self->split = strtok(self->line, " \n\t");
            if      (!strcmp(self->split, "1ps")) 
                self->timescale = 1e-12;
            else if (!strcmp(self->split, "10ps")) 
                self->timescale = 1e-11;
            else if (!strcmp(self->split, "100ps")) 
                self->timescale = 1e-10;
            else if (!strcmp(self->split, "1ns")) 
                self->timescale = 1e-9;
            else if (!strcmp(self->split, "10ns")) 
                self->timescale = 1e-8;
            else if (!strcmp(self->split, "100ns")) 
                self->timescale = 1e-7;
            else {
                self->timescale = 0.0;
            }
        }
    }
    printf("Timescale is %e.\n", self->timescale);
    // allocate space for nodes
    self->nodes = (vcd_node*)malloc(self->n_nodes * sizeof(vcd_node));
    if (!self->nodes) {
        fprintf(stderr, "malloc failed.\n");
        exit(-1);
    }
    fprintf(stdout, "Found %llu nodes.\n", self->n_nodes);
    // start again
    rewind(self->vcdfp);
    scope_top = 1;
    self->line_cnt = 0;
    while (fgets(self->line, VCD_LINE_MAX, self->vcdfp)) {
        self->line_cnt ++;

        /* end of header */
        if (0 == strcmp(self->line, "$enddefinitions $end\n"))
            break;

        /* $var - new variable */
        if (0 == strncmp(self->line, "$var", 4)) {
            VcdNodeCreate(&(self->nodes), &(self->line_cnt), self->line, scope, self->hier_separator);
        } else
        /* $scope - enter hierarchy level */
        if (0 == strncmp(self->line, "$scope", 6)) {
            /* $scope */
            self->split = strtok(self->line, " \n");
            /* module */
            self->split = strtok(0, " \n");
            /* scope name */
            self->split = strtok(0, " \n");
            if (scope_top == 1)
                scope_pos[scope_top] = strlen(self->split) + 1;
            else
                scope_pos[scope_top] = scope_pos[scope_top - 1] + strlen(self->split) + 1;
            scope_top++;
            sprintf(scope, "%s%c%s", scope, self->hier_separator, self->split);
        } else
        /* $upscope - leave hierarchy level */
        if (0 == strncmp(self->line, "$upscope", 8)) {
            scope[scope_pos[--scope_top-1]] = 0;
        }
    }
}

#endif // VCDPARSE_H
