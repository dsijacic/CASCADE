/* vcd2pff.h -- created by DS. */
#ifndef vcd2pff_H
#define vcd2pff_H

#include "defs.h"

#include "VcdNode.h"
#include "VcdNodeVector.h"
#include "frame.h"
#include "pff_wr.h"

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
);

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
);

void
Vcd2PffFinish(
    FILE**                              vcdFp,
    UI64                                vcdLineCnt,
    FILE**                              ioxFp,
    VcdNode**                           nodes
);

UI64 
Vcd2Pff_d_MSM_Power(
    FILE**                              vcdFp,
    FILE**                              ioxFp,
    
    const CHAR*                         file_name,

    const CHAR                          hier_separator,

    const CHAR*                         note,

    const UI32                          period,
    const UI32                          start,
    const UI32                          finish,

    const float                         distance
);

/*------------------------------------------------------------------------------
| End |
------------------------------------------------------------------------------*/

#endif //
