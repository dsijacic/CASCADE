/* pff_rd.c -- created by DS. */

#include "pff_rd.h"


/*------------------------------------------------------------------------------
| Defines |
------------------------------------------------------------------------------*/
void
PffReaderInit(
    PowerFrameFile*                     tgt
) {
    tgt->version = 0;
    tgt->note_len = 0;

    tgt->resolution = 0.0; 
    tgt->period = 0;
    tgt->start = 0;
    tgt->finish = 0;

    tgt->n_fi_bits = 0;
    tgt->n_fo_bits = 0;
    tgt->n_tgt_bits = 0;

    tgt->n_frames = 0;
    tgt->n_events = 0;

    tgt->buff_ = (UI08*)malloc(RW_BUFFER_SIZE);
    if (!tgt->buff_)
        exit(ERR_MALLOC);

    tgt->buff_wr_ = 0;
    tgt->buff_rd_ = 0;
}

void
PffReaderKill(
    PowerFrameFile*                     tgt
) {
    tgt->note_len = 0;
    if (tgt->note)
        free(tgt->note);
    tgt->note = 0;

    tgt->resolution = 0.0;
    tgt->period = 0;
    tgt->start = 0;
    tgt->finish = 0;

    tgt->n_fi_bits = 0;
    tgt->n_fo_bits = 0;
    tgt->n_tgt_bits = 0;

    tgt->n_frames = 0;
    tgt->n_events = 0;
    
    tgt->fp_ = 0;
    if (tgt->buff_)
        free(tgt->buff_);
    tgt->buff_ = 0;
    tgt->buff_rd_ = 0;
    tgt->buff_wr_ = 0;
}

void
PffReaderOpen(
    PowerFrameFile*                     tgt,
    const CHAR*                         file_name
) {
    tgt->fp_ = fopen(file_name, "rb");
    if (!tgt->fp_) 
        exit(ERR_IO);

    printf("Opened %s for reading.\n", file_name);
    fread(&tgt->version, sizeof(tgt->version), 1, tgt->fp_);
    fread(&tgt->note_len, sizeof(tgt->note_len), 1, tgt->fp_);
    if (tgt->note_len) {
        tgt->note = (CHAR*)malloc((tgt->note_len + 1) * sizeof(CHAR));
        if (!tgt->note)
            exit(ERR_MALLOC);
        fread(tgt->note, sizeof(CHAR), tgt->note_len, tgt->fp_);
        tgt->note[tgt->note_len] = 0;
    }

    fread(&tgt->resolution, sizeof(tgt->resolution), 1, tgt->fp_);
    fread(&tgt->period, sizeof(tgt->period), 1, tgt->fp_);
    fread(&tgt->start, sizeof(tgt->start), 1, tgt->fp_);
    fread(&tgt->finish, sizeof(tgt->finish), 1, tgt->fp_);
    
    fread(&tgt->n_fi_bits, sizeof(tgt->n_fi_bits ), 1, tgt->fp_);
    fread(&tgt->n_fo_bits, sizeof(tgt->n_fo_bits), 1, tgt->fp_);
    fread(&tgt->n_tgt_bits, sizeof(tgt->n_tgt_bits), 1, tgt->fp_);

    fread(&tgt->n_frames, sizeof(tgt->n_frames ), 1, tgt->fp_);
    fread(&tgt->n_events, sizeof(tgt->n_events ), 1, tgt->fp_);
    fread(&tgt->n_windows, sizeof(tgt->n_windows ), 1, tgt->fp_);

    // read first chunk of the file body into buffer
    tgt->buff_wr_ = fread(tgt->buff_, sizeof(UI08), RW_BUFFER_SIZE, tgt->fp_);
    tgt->buff_rd_ = 0;

    // display
    printf("%20s:%011x\n",  "Version",          tgt->version);
    printf("%20s: %s\n",    "Note",             tgt->note);
    printf("%20s: %e\n",    "Resolution",       tgt->resolution);
    printf("%20s:%11u\n",   "Period",           tgt->period);
    printf("%20s:%11u\n",   "Start",            tgt->start);
    printf("%20s:%11u\n",   "Finish",           tgt->finish);
    printf("%20s:%11u\n",   "Input bits",       tgt->n_fi_bits);
    printf("%20s:%11u\n",   "Output bits",      tgt->n_fo_bits);
    printf("%20s:%11u\n",   "Target bits",      tgt->n_tgt_bits);
    printf("%20s:%11u\n",   "Total frames",     tgt->n_frames);
    printf("%20s:%11u\n",   "Total events",     tgt->n_events);
    printf("%20s:%11u\n",   "Total windows",    tgt->n_windows);
}

void
PffReaderClose(
    PowerFrameFile*                     tgt
) {
    fclose(tgt->fp_);
    printf("Reader closed file.\n");
}

uint64_t
PffReadInitialState(
    PowerFrameFile*                     tgt,
    Frame*                              frame
) {
    uint64_t dec_len;
    
    dec_len =  PffReadFrame(tgt, frame);
    tgt->n_frames++;

    return dec_len;
}

uint64_t 
PffReadFrame(
    PowerFrameFile*                     tgt,
    Frame*                              frame
) {
    uint64_t dec_len;
    dec_len = FrameDecode(frame, &tgt->buff_[tgt->buff_rd_], tgt->buff_wr_ - tgt->buff_rd_);
    // first attempt to decode, it it returns zero, it means there is no space in the buffer
    if (!dec_len) {
        // copy the chunk of the frame on the beggining of the buffer and read more
        memcpy(
            tgt->buff_, 
            &tgt->buff_[tgt->buff_rd_], 
            tgt->buff_wr_ - tgt->buff_rd_
        );
        tgt->buff_wr_ = tgt->buff_wr_ - tgt->buff_rd_;
        tgt->buff_rd_ = 0;
        // fill buffer with more data from file
        tgt->buff_wr_ += 
            fread(
                &tgt->buff_[tgt->buff_wr_], 
                sizeof(UI08), 
                RW_BUFFER_SIZE - tgt->buff_wr_,
                tgt->fp_
            );
        // try  to decode again, it it fails now, it means that buffer can not fit the frame
        dec_len = FrameDecode(frame, &tgt->buff_[tgt->buff_rd_], tgt->buff_wr_ - tgt->buff_rd_);
        if (!dec_len) {
            fprintf(stderr, "RW_BUFFER_SIZE = %lu < Frame.byte_size = %lu.\n", RW_BUFFER_SIZE, frame->byte_size + sizeof(frame->byte_size));
            exit(ERR_EXCESS); // TODO return 0 here can be used to dump everythin processed up to that point
        } 
        
    }
    tgt->buff_rd_ += dec_len;
    tgt->n_frames--;
    tgt->n_events -= frame->n_events;

    return tgt->buff_rd_;
}

