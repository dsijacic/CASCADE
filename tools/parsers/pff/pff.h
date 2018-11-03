/* pff.h -- created by DS. */
/* *.pff format 
Binary format for storing power frames. 
struct {
        UI32                            version;
        UI32                            note_len;
        CHAR*                           note;

        FL32                            resolution;
        UI32                            period;
        UI64                            start;
        UI64                            finish;

        UI16                            n_fi_bits;
        UI16                            n_fo_bits;
        UI16                            n_tgt_bits;

        UI32                            n_frames;
        UI32                            n_events;
        UI32                            n_windows;

        FRAME                           frames<n_frames>;
} *.pff
*/

#ifndef pff_H
#define pff_H

#include <defs.h>

typedef struct power_frame_file         PowerFrameFile;

struct power_frame_file {
        UI32                            version;
        UI32                            note_len;
        CHAR*                           note;

        FL32                            resolution;
        UI32                            period;
        UI64                            start;
        UI64                            finish;

        UI16                            n_fi_bits;
        UI16                            n_fo_bits;
        UI16                            n_tgt_bits;

        UI32                            n_frames;
        UI32                            n_events;
        UI32                            n_windows;

        // frames
        // FRAME                        frames<n_frames>;
        // because of large file sizes Frame* frames is not in this structure
        // instead once created frames will be dirrectly encoded and written to
        // an actual file on disk

        // I/O control
        FILE*                           fp_;
        UI08*                           buff_;
        UI64                            buff_rd_;
        UI64                            buff_wr_;
};

#endif //
