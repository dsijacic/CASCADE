/* pff_reader.h -- created by DS. */
#ifndef pff_reader_H
#define pff_reader_H

#include "defs.h"
#include "pff.h"
#include "frame.h"

#include <string.h>

void
PffReaderInit(
    PowerFrameFile*                     tgt
);

void
PffReaderKill(
    PowerFrameFile*                     tgt
);

void
PffReaderOpen(
    PowerFrameFile*                     tgt,
    const CHAR*                         file_name
);

void
PffReaderClose(
    PowerFrameFile*                     tgt
);

void
PffReaderPeek(
    PowerFrameFile*                     tgt,
    const CHAR*                         file_name
);

UI64
PffReadFrame(
    PowerFrameFile*                     tgt,
    Frame*                              frame
);

// obsolete
UI64
PffReadInitialState(
    PowerFrameFile*                     tgt,
    Frame*                              frame
);

#endif //
