/* vcd2pff.c -- created by DS. */

#include "defs.h"
#include "vcd2pff.h"

ERR_CODE 
Vcd2PffSetup(
    CHAR*                               vcdFile,
    CHAR*                               ioxFile,

    Frame*                              workingFrame,
    VcdNodeVector*                      excludedNodes,

    const CHAR                          hierSeparator,
    FLAG                                useTrigger,
    CHAR*                               trigger,
    VcdNode*                            triggerNode,
    FLAG*                               triggerFound,

    FILE**                              vcdFp,
    FILE**                              ioxFp,
    UI64*                               vcdLineCnt,
    FL32*                               resolution,
    VcdNode**                           nodes
) {

    CHAR* line = (CHAR*)malloc(MAX_LINE_SIZE * sizeof(CHAR));
    if (!line) 
        return ERR_MALLOC;

    CHAR* auxl = (CHAR*)malloc(MAX_LINE_SIZE * sizeof(CHAR));
    if (!auxl) 
        return ERR_MALLOC;

    CHAR* scope = (CHAR*)malloc(MAX_LINE_SIZE * sizeof(CHAR));
    if (!scope) 
        return ERR_MALLOC;

    CHAR* split;

    UI08 scope_pos[256] = {0}; // allows 256 levels of hierarchy
    UI08 scope_top;

    UI64 n_nodes, i, j;

    /* ###################################################################### */
    /* Parse VCD header in two itterations.                                   */
    /* ###################################################################### */

    /* Open VCD file. */
    *vcdFp = fopen(vcdFile, "r");
    if (!(*vcdFp)) {
        fprintf(stderr, "\tvcd2pff:\n\t+ Can not open file %s\n", vcdFile);
        return ERR_IO;
    }
    else {
        fprintf(stdout, "Opened %s for reading.\n", vcdFile);
    }

    /* 1. Count nodes                                                         */
    n_nodes = 0;

    while (fgets(line, MAX_LINE_SIZE, *vcdFp)) {
        if (0 == strcmp(line, "$enddefinitions $end\n"))
            break;

        if (!strncmp(line, "$var", 4)) {
            n_nodes++;
        }

        if (!strncmp(line, "$timescale", 10)) {
            fgets(line, MAX_LINE_SIZE, *vcdFp);
            split = strtok(line, " \n\t");
            if      (!strcmp(split, "1ps")) 
                *resolution = 1e-12;
            else if (!strcmp(split, "10ps")) 
                *resolution = 1e-11;
            else if (!strcmp(split, "100ps")) 
                *resolution = 1e-10;
            else if (!strcmp(split, "1ns")) 
                *resolution = 1e-9;
            else if (!strcmp(split, "10ns")) 
                *resolution = 1e-8;
            else if (!strcmp(split, "100ns")) 
                *resolution = 1e-7;
            else if (!strcmp(split, "1us")) 
                *resolution = 1e-6;
            else {
                fprintf(stderr, "\tvcd2pff:\n\t+ Unsupproted resolution (timescale) %s.\n", split);
                exit(ERR_VALUE);
            }
        }
    }

    fprintf(stdout, "Found %llu nodes.\n", n_nodes);
    fprintf(stdout, "Time scale is %e seconds.\n", *resolution);

    /* 2. Parse nodes                                                         */
    rewind(*vcdFp);

    *nodes = (VcdNode*)malloc(n_nodes*sizeof(VcdNode));
    if (!(*nodes))
        exit(ERR_MALLOC);

    scope_top = 1;
    *vcdLineCnt = 0;

    while (fgets(line, MAX_LINE_SIZE, *vcdFp)) {

        (*vcdLineCnt)++;

        if (0 == strcmp(line, "$enddefinitions $end\n"))
            break;

        /* $var - new variable */
        if (0 == strncmp(line, "$var", 4)) {
            VcdNodeCreate(nodes, line, scope, hierSeparator);
        } else

        /* $scope - enter hierarchy level */
        if (0 == strncmp(line, "$scope", 6)) {
            /* $scope */
            split = strtok(line, " \n");
            /* module */
            split = strtok(0, " \n");
            /* scope name */
            split = strtok(0, " \n");
            if (scope_top == 1)
                scope_pos[scope_top] = strlen(split) + 1;
            else
                scope_pos[scope_top] = scope_pos[scope_top - 1] + strlen(split) + 1;
            scope_top++;
            sprintf(scope, "%s%c%s", scope, hierSeparator, split);
        } else
        /* $upscope - leave hierarchy level */
        if (0 == strncmp(line, "$upscope", 8)) {
            scope[scope_pos[--scope_top-1]] = 0;
        }
    }

    /* check if trigger is there */
    if (useTrigger) {
        if (!trigger) {
            fprintf(stderr, "\tvcd2pff:\n\t+ Must specify trigger name!\n");
            return ERR_ARGS;
        }
        *triggerFound = 0;
        for (i = 0; i < n_nodes; i++) {
            // printf("-> %s\n", (*nodes)[i].name);
            if (0 == strcmp((*nodes)[i].name, trigger)) {
                *triggerFound = 1;
                triggerNode = &(*nodes)[i];
                fprintf(stdout, "Found trigger %s!\n", trigger);
                break;
            }
        }
        if (!(*triggerFound)) {
            fprintf(stderr, "\tvcd2pff:\n\t+ Trigger %s not found in the VCD file! \n", trigger);
            return ERR_MISS;
        }
    } else {
        fprintf(stdout, "Not using trigger.\n");
    }

    /* ###################################################################### */
    /* Parse the port mapping (IOX)       .                                   */
    /* ###################################################################### */

    *ioxFp = fopen(ioxFile, "r");
    if (!(*ioxFp)) {
        fprintf(stderr, "\tvcd2pff:\n\t+ Can not open file %s\n", ioxFile);
        return ERR_IO;
    }
    else {
        fprintf(stdout, "Opened %s for reading.\n", ioxFile);
    }

    UI16 finBits = 0;
    UI16 fotBits = 0;
    UI16 excBits = 0;
    UI16 tgtBits = 0;
    UI16 width   = 0;

    while (fgets(line, MAX_LINE_SIZE, *ioxFp)) {
        if (line[0] == '#' || line[0] == '\n')
            continue;

        split = strtok(line, " \n");
        /* frame inputs */
        if (0 == strcmp(split, "fin")) {
            split = strtok(0, " \n");
            finBits += atoi(split);
        } else
        /* frame outputs */
        if (0 == strcmp(split, "fot")) {
            split = strtok(0, " \n");
            fotBits += atoi(split);
        } else 
        /* exclude power from nodes */
        if (0 == strcmp(split, "exc")) {
            split = strtok(0, " \n");
            excBits += atoi(split);
        } else
        /* target bits */
        if (0 == strcmp(split, "tgt")) {
            split = strtok(0, " \n");
            tgtBits += atoi(split);
        }
        else {
            /* invalid line */
            fprintf(stderr, "\tvcd2pff:\n\t+ Invalid *.iox line %s", line);
            return ERR_PARSING;
        }
    }

    rewind(*ioxFp);

    /* Prepare frame vectors */

    FLAG nodeFound;

    FrameInit(workingFrame, finBits, fotBits, tgtBits);
    VcdNodeVectorInit(excludedNodes, excBits);

    // for (i = 0; i<n_nodes; i++) printf("! %s\n", (*nodes)[i].name);

    while (fgets(line, MAX_LINE_SIZE, *ioxFp)) {

        if (line[0] == '#' || line[0] == '\n')
            continue;

        nodeFound = 0;
        // printf(">>> %s", line);
        split = strtok(line, " \n");
        /* frame input vector */
        if (0 == strcmp(split, "fin")) {
            split = strtok(0, " \n");
            width = atoi(split);
            split = strtok(0, " \n");
            for (i=0; i < n_nodes; i++) {
                /* check if name mathes nodes from VCD file directly */
                if (0 == strcmp((*nodes)[i].name, split)) {
                    VcdNodeVectorBindNode(&workingFrame->fi, &(*nodes)[i]);
                    nodeFound = 1;
                    break;
                } 
                else {
                    for(j = width; j > 0; j--) {
                        sprintf(auxl, "%s[%llu]", split, j-1);
                        if (0 == strcmp((*nodes)[i].name, auxl)) {
                            VcdNodeVectorBindNode(&workingFrame->fi, &(*nodes)[i]);
                            nodeFound = 1;
                            break;
                        }
                    }
                }
            }
        } else
        /* frame output vector */
        if (0 == strcmp(split, "fot")) {
            split = strtok(0, " \n");
            width = atoi(split);
            split = strtok(0, " \n");
            for (i=0; i < n_nodes; i++) {
                /* check if name mathes nodes from VCD file directly */
                if (0 == strcmp((*nodes)[i].name, split)) {
                    VcdNodeVectorBindNode(&workingFrame->fo, &(*nodes)[i]);
                    nodeFound = 1;
                    break;
                } 
                else {
                    for(j = width; j > 0; j--) {
                        sprintf(auxl, "%s[%llu]", split, j-1);
                        if (0 == strcmp((*nodes)[i].name, auxl)) {
                            VcdNodeVectorBindNode(&workingFrame->fo, &(*nodes)[i]);
                            nodeFound = 1;
                            break;
                        }
                    }
                }
            }
        } else
        /* target vector */
        if (0 == strcmp(split, "tgt")) {
            split = strtok(0, " \n");
            width = atoi(split);
            split = strtok(0, " \n");
            for (i=0; i < n_nodes; i++) {
                /* check if name mathes nodes from VCD file directly */
                if (0 == strcmp((*nodes)[i].name, split)) {
                    VcdNodeVectorBindNode(&workingFrame->tgt, &(*nodes)[i]);
                    nodeFound = 1;
                    break;
                } 
                else {
                    for(j = width; j > 0; j--) {
                        sprintf(auxl, "%s[%llu]", split, j-1);
                        if (0 == strcmp((*nodes)[i].name, auxl)) {
                            VcdNodeVectorBindNode(&workingFrame->tgt, &(*nodes)[i]);
                            nodeFound = 1;
                            break;
                        }
                    }
                }
            }
        } else
        /* exclude vector */
        if (0 == strcmp(split, "exc")) {
            split = strtok(0, " \n");
            width = atoi(split);
            split = strtok(0, " \n");
            for (i=0; i < n_nodes; i++) {
                /* check if name mathes nodes from VCD file directly */
                if (0 == strcmp((*nodes)[i].name, split)) {
                    VcdNodeVectorBindNode(excludedNodes, &(*nodes)[i]);
                    nodeFound = 1;
                    break;
                } 
                else {
                    for(j = width; j > 0; j--) {
                        sprintf(auxl, "%s[%llu]", split, j-1);
                        if (0 == strcmp((*nodes)[i].name, auxl)) {
                            VcdNodeVectorBindNode(excludedNodes, &(*nodes)[i]);
                            nodeFound = 1;
                            break;
                        }
                    }
                }
            }
        }
    }

    // finalize nodes
    VcdNodeVectorFinalize(&workingFrame->fi, "fin");
    VcdNodeVectorFinalize(&workingFrame->fo, "fot");
    VcdNodeVectorFinalize(&workingFrame->tgt, "tgt");
    VcdNodeVectorFinalize(excludedNodes, "exc");

    if (line) free(line); line = 0;
    if (auxl) free(auxl); auxl = 0;
    if (scope) free(scope); scope = 0;

    return ERR_SUCCESS;
}

void
Vcd2PffFinish(
    FILE**                              vcdFp,
    UI64                                vcdLineCnt,
    FILE**                              ioxFp,
    VcdNode**                           nodes
) {
    if (*vcdFp) 
        fclose(*vcdFp);
    if (*ioxFp) 
        fclose(*ioxFp);
    if (*nodes) 
        free(*nodes);
    *nodes = 0;
    fprintf(stdout, "Parsed %llu lines of a VCD file.\n", vcdLineCnt);
}

ERR_CODE
Vcd2PffRun(
    PowerFrameFile*                     pff,
    FILE**                              vcdFp,
    Frame*                              frame,

    VcdNode**                           nodes,
    VcdNodeVector*                      excludedNodes,
    VcdNode*                            triggerNode,
    FLAG                                useTrigger,
    UI64*                               start,
    UI64*                               finish,
    UI64*                               vcdLineCnt,
    UI32                                period,
    FL32                                switchingDistance
) {
    UI32 timeInFrame = 0;
    UI64 eventTime = 0;
    UI64 startTime = 0;
    UI64 currTime = 0;
    UI32 eventValue = 0; // must convert to FL32 prior to storing
    FLAG triggered = 0;

    CHAR* line = (CHAR*)malloc(MAX_LINE_SIZE * sizeof(CHAR));
    if (!line) 
        return ERR_MALLOC;
    if (useTrigger) {
        fprintf(stderr, "\t+ Triggering is under maintenance...\n");
        return ERR_GENERAL;
        // /* initialize simulation without evaluating power */
        // while (fgets(line, MAX_LINE_SIZE, *vcdFp)) {
        //     // printf("> %llu: %s", *vcdLineCnt, line);
        //     (*vcdLineCnt)++;

        //     if (VcdNodeGetBit(triggerNode)) {
        //         /* trigger is set, start the processing */
        //         triggered = 1;
        //         *start = currTime;
        //         eventTime = currTime;
        //         /* evaluate the initial conditions of the frame vectors */
        //         VcdNodeVectorEvaluate(&frame->fi);
        //         VcdNodeVectorEvaluate(&frame->fo);
        //         VcdNodeVectorEvaluate(&frame->tgt);
        //         break;
        //     } else {
        //         if (*finish && (currTime >= *finish)) {
                    
        //         }
        //     }
        //     if (line[0] == '#') {
        //         /* time value */
        //         currTime = strtoull(&line[1], 0, 10);

        //     } else
        //     if ((0 == strcmp(line, "$dumpvars\n") || (0 == strcmp(line, "$end\n"  )))) {
        //         /* skip */
        //         continue;
        //     } else 
        //     {
        //         /* set node value from line */
        //         VcdNodeSetValue(nodes, line);
        //     }
        // }
    } else {
        /* initialize simulation without evaluating power */
        pff->n_windows = 1;
        while (fgets(line, MAX_LINE_SIZE, *vcdFp)) {
            // printf("> %llu: %s", *vcdLineCnt, line);
            (*vcdLineCnt)++;
            if (line[0] == '#') {
                currTime = strtoull(&line[1], 0, 10);
                if (currTime >= *start) {
                    startTime = currTime;
                    pff->start = startTime;
                    // printf("pff->start = %lu\n", pff->start);
                    eventTime = currTime;
                    /* evaluate the initial conditions of the frame vectors */
                    VcdNodeVectorEvaluate(&frame->fi);
                    VcdNodeVectorEvaluate(&frame->fo);
                    VcdNodeVectorEvaluate(&frame->tgt);
                    break;
                }
            } else if (0 == strcmp(line, "$dumpvars\n")) {
                continue;
            } else if (0 == strcmp(line, "$end\n")) {
                continue;
            } else {
                VcdNodeSetValue(nodes, line);
            }
        }
        // fprintf(stdout, "\t+ First frame begins at sample %llu.\n", startTime);
        while (fgets(line, MAX_LINE_SIZE, *vcdFp)) {
            (*vcdLineCnt)++;
            if (line[0] == '#') {
                 // printf("+q %llu: %s", *vcdLineCnt, line);
                /* new time moment in the simulation */
                currTime = strtoull(&line[1], 0, 10);
                /* preemptive finish */
                // if (*finish && currTime > *finish) 
                //     break;
                // fprintf(stdout, "currTime = %llu!\n", currTime);
                /* write previous event if it is significant; update event time */
                if (eventValue != 0) {
                    timeInFrame = (uint32_t)((eventTime - startTime) % ((uint64_t)period));
                    // printf("%llu timeInFrame %lu\n", *vcdLineCnt, timeInFrame);
                    FrameAddEvent(frame, timeInFrame, (FL32)eventValue);
                    eventValue = 0;
                }
                eventTime = currTime;

                /* check if it is time for a new frame */
                if (!((currTime - startTime) % ((uint64_t)period))) {
                    // evaluate frame values
                    VcdNodeVectorEvaluate(&frame->fi);
                    VcdNodeVectorEvaluate(&frame->fo);
                    VcdNodeVectorEvaluate(&frame->tgt);
                    PffWriteFrame(pff, frame);
                    FrameClearEvents(frame);
                }
            } else {
                /* evaluate power of a toggle in a frame; also updates the frame value */
                eventValue += VcdNodeUpdate_d_MSM(nodes, line, switchingDistance, excludedNodes->vcd_nodes, excludedNodes->_n_nodes);
            }
        }
        if (frame->n_events) {
            /* Dump whatever is found at the end, it can easily be ignored/removed later */
            // evaluate frame values
            VcdNodeVectorEvaluate(&frame->fi);
            VcdNodeVectorEvaluate(&frame->fo);
            VcdNodeVectorEvaluate(&frame->tgt);
            PffWriteFrame(pff, frame);
            FrameClearEvents(frame);
        }
    }
    pff->finish = currTime;
    printf("Parsed %llu lines of a VCD file.\n", vcdLineCnt);
    if (line) free(line); line = 0;

    return ERR_SUCCESS;
}