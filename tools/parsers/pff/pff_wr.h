/* pff_writer.h -- created by DS. */
#ifndef pff_writer_H
#define pff_writer_H

#include "defs.h"
#include "pff.h"
#include "frame.h"

ERR_CODE
PffWriterInit(
    PowerFrameFile*                     tgt,
    const UI32                          version,
    const CHAR*                         note,
    const FL32                          resolution,
    const UI32                          period,
    const UI16                          n_fi_bits,
    const UI16                          n_fo_bits,
    const UI16                          n_tgt_bits
);

ERR_CODE
PffWriterKill(
    PowerFrameFile*                     tgt
);

ERR_CODE
PffWriterOpen(
    PowerFrameFile*                     tgt,
    const CHAR*                         file_name
);

void
PffWriterClose(
    PowerFrameFile*                     tgt
);

UI64
PffWriteFrame(
    PowerFrameFile*                     tgt,
    Frame*                              frame
);

// obsolete
UI64
PffWriteInitialState(
    PowerFrameFile*                     tgt,
    Frame*                              frame,
    const UI32                          start_time
);

#endif //
