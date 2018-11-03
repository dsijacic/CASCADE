/* frame.h -- created by DS. */
#ifndef frame_H
#define frame_H

#include "VcdNodeVector.h"

#include <defs.h>
// #include <stdlib.h>
// #include <stdio.h>
// #include <stdint.h>

typedef struct Frame Frame;

struct Frame{
    UI32                                byte_size;
    UI32                                frame_cnt;

    VcdNodeVector                       fi;
    VcdNodeVector                       fo;
    VcdNodeVector                       tgt;
    UI32                                n_events;
    UI32*                               t_events;
    FL32*                               v_events;

    UI32                                a_events_;
};

void
FrameInit(
    Frame*                              tgt,
    const UI16                          n_fi_bits,
    const UI16                          n_fo_bits,
    const UI16                          n_tgt_bits
);

void
FrameKill(
    Frame*                              tgt
);

void 
FrameToString(
    const Frame*                        tgt,
    const UI32                          indent
);

void
FrameAddEvent(
    Frame*                              tgt,
    UI32                                t_event,
    FL32                                v_event
);

void
FrameClearEvents(
    Frame*                              tgt
);

void
FrameEvaluate(
    Frame*                              tgt
);


UI64
FrameEncode(
    Frame*                              tgt,
    UI08*                               buff,
    const UI64                          buff_size
);

UI64
FrameDecode(
    Frame*                              tgt,
    const UI08*                         buff,
    const UI64                          buff_size
);

UI64
FrameSize(
    Frame*                              tgt
);


#endif //
