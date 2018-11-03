/* pff_peak.c -- created by DS. */

#include "defs.h"
#include "pff_rd.h"
#include "frame.h"

#include <stdio.h>

int main(int argc, char** argv) {

    UI64 cnt;
    UI32 n_frames;

    if (argc < 2) {
        fprintf(stderr, "pff_peak <*.pff> [n_frames]\n");
        return -1;
    } else if (argc == 2) {
        n_frames = 1;
    } else {
        n_frames = strtoul(argv[3], 0, 0);
    }

    PowerFrameFile pff;
    Frame frame;

    PffReaderInit(&pff);
    printf("--- Peaking in %s ---\n", argv[2]);
    PffReaderOpen(&pff, argv[2]);
    FrameInit(&frame, pff.n_fi_bits, pff.n_fo_bits, pff.n_tgt_bits);
    PffReadInitialState(&pff, &frame);
    printf("---\n");
    printf("Initial:\n");
    printf("FI:  "); VcdNodeVectorToString(&frame.fi, 0);
    printf("FO:  "); VcdNodeVectorToString(&frame.fo, 0);
    printf("TGT: "); VcdNodeVectorToString(&frame.tgt, 0);

    for (cnt = 0; cnt < n_frames; cnt++) {
        PffReadFrame(&pff, &frame);
        printf("---\n");
        printf("Frame #%lu:\n", cnt + 1);
        printf("FI:  "); VcdNodeVectorToString(&frame.fi, 0);
        printf("FO:  "); VcdNodeVectorToString(&frame.fo, 0);
        printf("TGT: "); VcdNodeVectorToString(&frame.tgt, 0);
    }
    printf("---\n");
    FrameKill(&frame);
    PffReaderClose(&pff);
    PffReaderKill(&pff);
}
// void
// PffReaderPeek(
//     PowerFrameFile*                     tgt,
//     const char*                         file_name
// ) {
//     uint64_t i;
//     PffReaderInit(tgt);
//     printf("---\n");
//     PffReaderOpen(tgt, file_name);
//     Frame frame;
//     FrameInit(&frame, tgt->n_fi_bits, tgt->n_fo_bits);
//     PffReadInitialState(tgt, &frame);
//     printf("---\n");
//     printf("Initial state:\n");
//     printf("FI: "); VcdNodeVectorToString(&frame.fi, 0);
//     printf("FO: "); VcdNodeVectorToString(&frame.fo, 0);
//     printf("---\n");
//     printf("Final state:\n");
//     while (tgt->n_frames > 0) {
//         PffReadFrame(tgt, &frame);
//     }
//     printf("FI: "); VcdNodeVectorToString(&frame.fi, 0);
//     printf("FO: "); VcdNodeVectorToString(&frame.fo, 0);
//     printf("---\n");
//     FrameKill(&frame);
//     PffReaderClose(tgt);
//     PffReaderKill(tgt);
// }
//     PffReaderPeek(&pff, argv[1]);
// }
