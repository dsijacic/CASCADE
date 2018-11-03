/* pff_writer.c -- created by DS. */

#include "pff_wr.h"

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
) {
    if (note) {
        tgt->note_len = strlen(note);
        tgt->note = note;
    } else {
        tgt->note_len = 0;
        tgt->note = 0;
    }
    tgt->version = version;
    tgt->resolution = resolution; 
    tgt->period = period;
    tgt->start = 0;
    tgt->finish = 0;

    tgt->n_fi_bits = n_fi_bits;
    tgt->n_fo_bits = n_fo_bits;
    tgt->n_tgt_bits = n_tgt_bits;

    tgt->n_frames = 0;
    tgt->n_events = 0;

    tgt->buff_ = (UI08*)malloc(RW_BUFFER_SIZE);
    if (!tgt->buff_)
        return ERR_MALLOC;

    tgt->buff_wr_ = 0;
    tgt->buff_rd_ = 0;

    return ERR_SUCCESS;
}

ERR_CODE
PffWriterKill(
    PowerFrameFile*                     tgt
) {
    tgt->note_len = 0;
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

    return ERR_SUCCESS;
}

ERR_CODE
PffWriterOpen(
    PowerFrameFile*                     tgt,
    const char*                         file_name
) {
    tgt->fp_ = fopen(file_name, "wb");
    if (!tgt->fp_) 
        return ERR_IO;

    printf("Opened %s for writting.\n", file_name);
    fwrite(&tgt->version, sizeof(tgt->version), 1, tgt->fp_);
    fwrite(&tgt->note_len, sizeof(tgt->note_len), 1, tgt->fp_);
    if (tgt->note_len)
        fwrite( tgt->note, sizeof(CHAR), tgt->note_len, tgt->fp_);
    fwrite(&tgt->resolution, sizeof(tgt->resolution), 1, tgt->fp_);
    fwrite(&tgt->period, sizeof(tgt->period), 1, tgt->fp_);
    fwrite(&tgt->start, sizeof(tgt->start), 1, tgt->fp_);
    fwrite(&tgt->finish, sizeof(tgt->finish), 1, tgt->fp_);
    fwrite(&tgt->n_fi_bits, sizeof(tgt->n_fi_bits ), 1, tgt->fp_);
    fwrite(&tgt->n_fo_bits, sizeof(tgt->n_fo_bits), 1, tgt->fp_);
    fwrite(&tgt->n_tgt_bits, sizeof(tgt->n_tgt_bits), 1, tgt->fp_);
    fwrite(&tgt->n_frames, sizeof(tgt->n_frames), 1, tgt->fp_);
    fwrite(&tgt->n_events, sizeof(tgt->n_events), 1, tgt->fp_);
    fwrite(&tgt->n_windows, sizeof(tgt->n_windows), 1, tgt->fp_);

    if (tgt->note)
        printf("%20s: %s\n",    "Note",             tgt->note);
    else
        printf("%20s: %s\n",    "Note",             "n/a");
    printf("%20s: %e\n",    "Resolution",       tgt->resolution);
    printf("%20s:%11u\n",   "Period",           tgt->period);
    printf("%20s:%11u\n",   "Input bits",       tgt->n_fi_bits);
    printf("%20s:%11u\n",   "Output bits",      tgt->n_fo_bits);
    printf("%20s:%11u\n",   "Target bits",      tgt->n_tgt_bits);

    return ERR_SUCCESS;
}

void
PffWriterClose(
    PowerFrameFile*                     tgt
) {
    // flush any remaining frames in the I/O buffer to file
    if (tgt->buff_wr_ > 0) {
        fwrite(tgt->buff_, sizeof(UI08), tgt->buff_wr_, tgt->fp_);
        tgt->buff_wr_ = 0;
    }
    // rewind and update total number of frames and events
        fseek(tgt->fp_, 
            sizeof(tgt->note_len) + tgt->note_len +
            sizeof(tgt->resolution) +
            sizeof(tgt->period),
            SEEK_SET
        );
        fwrite(&tgt->start, sizeof(tgt->start), 1, tgt->fp_);
        fwrite(&tgt->finish, sizeof(tgt->finish), 1, tgt->fp_);
        fseek(tgt->fp_,
            sizeof(tgt->n_fi_bits) +
            sizeof(tgt->n_fo_bits) +
            sizeof(tgt->n_tgt_bits),
            SEEK_CUR
        );
        fwrite(&tgt->n_frames, sizeof(tgt->n_frames), 1, tgt->fp_);
        fwrite(&tgt->n_events, sizeof(tgt->n_events), 1, tgt->fp_);
        fwrite(&tgt->n_windows, sizeof(tgt->n_windows), 1, tgt->fp_);
    // close the file
    fclose(tgt->fp_);

    // display
    printf("%20s:%11u\n",   "Start",            tgt->start);
    printf("%20s:%11u\n",   "Finish",           tgt->finish);
    printf("%20s:%11u\n",   "Total frames",     tgt->n_frames);
    printf("%20s:%11u\n",   "Total events",     tgt->n_events);
    printf("%20s:%11u\n",   "Total windows",    tgt->n_windows);

    printf("File closed.\n");
}

UI64 
PffWriteFrame(
    PowerFrameFile*                     tgt,
    Frame*                              frame
) {
    UI64 enc_len;
    enc_len = FrameEncode(frame, &tgt->buff_[tgt->buff_wr_], RW_BUFFER_SIZE - tgt->buff_wr_);
    if (!enc_len) {
        // flush contents of the buffer
        fwrite(tgt->buff_, sizeof(UI08), tgt->buff_wr_, tgt->fp_);
        tgt->buff_wr_ = 0;
        // attempt to encode again
        enc_len = FrameEncode(frame, &tgt->buff_[tgt->buff_wr_], RW_BUFFER_SIZE - tgt->buff_wr_);
        if (!enc_len) {
            fprintf(stderr, "RW_BUFFER_SIZE = %lu < Frame.byte_size = %lu.\n", RW_BUFFER_SIZE, frame->byte_size + sizeof(frame->byte_size));
            exit(ERR_EXCESS); // TODO return 0 here can be used to dump everythin processed up to that point
        }
    }
    tgt->buff_wr_ += enc_len;
    tgt->n_frames ++;
    tgt->n_events += frame->n_events;
    return tgt->buff_wr_;
}

UI64
PffWriteInitialState(
    PowerFrameFile*                     tgt,
    Frame*                              frame,
    const UI32                          start_time
) {
    UI64 enc_len;

    enc_len = PffWriteFrame(tgt, frame);

    tgt->n_frames--;
    tgt->start = start_time;

    printf("%20s:%11u\n",   "Start",            tgt->start);

    tgt->n_windows = 1;
    return enc_len;
}

