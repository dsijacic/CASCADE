/* frame.c -- created by DS. */

#include "frame.h"

void
FrameInit(
    Frame*                              tgt,
    const UI16                          n_fi_bits,
    const UI16                          n_fo_bits,
    const UI16                          n_tgt_bits
) {
    tgt->byte_size = 0;
    tgt->frame_cnt = 0;
    VcdNodeVectorInit(&tgt->fi, n_fi_bits);
    VcdNodeVectorInit(&tgt->fo, n_fo_bits);
    VcdNodeVectorInit(&tgt->tgt, n_tgt_bits);
    tgt->n_events = 0;
    tgt->a_events_ = FRAME_MIN_ALLOC_EVENTS;
    tgt->t_events = (UI32*)malloc(tgt->a_events_ * sizeof(UI32));
    tgt->v_events = (FL32*)malloc(tgt->a_events_ * sizeof(FL32));
    if (!(tgt->t_events && tgt->v_events)) {
        fprintf(stderr, "@FrameInit: Memory allocation failed!\n");
        exit(-1);        
    }
}

void
FrameKill(
    Frame*                              tgt
) {
    tgt->byte_size = 0;
    tgt->frame_cnt = 0;

    VcdNodeVectorKill(&tgt->fi);
    VcdNodeVectorKill(&tgt->fo);
    VcdNodeVectorKill(&tgt->tgt);

    tgt->n_events = 0;
    tgt->a_events_ = 0;

    if (tgt->t_events) 
        free(tgt->t_events);
    tgt->t_events = 0;
    if (tgt->v_events) 
        free(tgt->v_events);
    tgt->v_events = 0;
}

void 
FrameToString(
    const Frame*                        tgt,
    const UI32                          indent
) {
    UI32 j, i;
    for (i = 0; i < indent; i++) printf(".."); 
    printf("#: %lu\n", tgt->frame_cnt);
    for (i = 0; i < indent; i++) printf(".."); 
    printf("FI:  "); VcdNodeVectorToString(&tgt->fi, 0); 
    for (i = 0; i < indent; i++) printf(".."); 
    printf("FO:  "); VcdNodeVectorToString(&tgt->fo, 0);
    for (i = 0; i < indent; i++) printf(".."); 
    printf("TGT: "); VcdNodeVectorToString(&tgt->tgt, 0);
    for (i = 0; i < indent; i++) printf(".."); 
    printf("#Events: %u\n", tgt->n_events);
    for (j=0; j<tgt->n_events; j++) {
        for (i = 0; i < indent+1; i++) printf(".."); 
        printf("%08x %f\n", tgt->t_events[j], tgt->v_events[j]);
    }
}

void
FrameAddEvent(
    Frame*                              tgt,
    UI32                                t_event,
    FL32                                v_event
) {
    if (tgt->n_events >= tgt->a_events_) {
        tgt->a_events_ += FRAME_MIN_ALLOC_EVENTS; 
        tgt->t_events = (UI32*)realloc(tgt->t_events, tgt->a_events_ * sizeof(UI32));
        if (!tgt->t_events) {
            fprintf(stderr, "@FrameUpdate: Memory realloc failed!\n");
            exit(-1);
        }
        tgt->v_events = (FL32*)realloc(tgt->v_events, tgt->a_events_ * sizeof(FL32));
        if (!tgt->v_events) {
            fprintf(stderr, "@FrameUpdate: Memory realloc failed!\n");
            exit(-1);
        }
    }
    tgt->t_events[tgt->n_events] = t_event;
    tgt->v_events[tgt->n_events] = v_event;
    tgt->n_events++;
}

void
FrameClearEvents(
    Frame*                              tgt
) {
    tgt->n_events = 0;
}

void
FrameEvaluate(
    Frame*                              tgt
) {
    VcdNodeVectorEvaluate(&tgt->fi);
    VcdNodeVectorEvaluate(&tgt->fo);
    VcdNodeVectorEvaluate(&tgt->tgt);
}

UI64
FrameEncode(
    Frame*                              tgt,
    UI08*                               buff,
    const UI64                          buff_size
) {
    UI64 i;
    UI64 enc_len;
    UI08* enc_p;

    if (buff_size < FrameSize(tgt) + sizeof(tgt->byte_size)) {
        return 0;
    }
    enc_len = 0;

    // byte size 
    buff[enc_len++] = tgt->byte_size;
    buff[enc_len++] = tgt->byte_size >> 8 & 0xff;
    buff[enc_len++] = tgt->byte_size >> 16 & 0xff;
    buff[enc_len++] = tgt->byte_size >> 24 & 0xff;
    // frame_cnt
    buff[enc_len++] = tgt->frame_cnt;
    buff[enc_len++] = tgt->frame_cnt >> 8 & 0xff;
    buff[enc_len++] = tgt->frame_cnt >> 16 & 0xff;
    buff[enc_len++] = tgt->frame_cnt >> 24 & 0xff;
    // io
    enc_len += VcdNodeVectorEncode(&tgt->fi, &buff[enc_len]);
    enc_len += VcdNodeVectorEncode(&tgt->fo, &buff[enc_len]);
    enc_len += VcdNodeVectorEncode(&tgt->tgt, &buff[enc_len]);
    // n_events
    buff[enc_len++] = tgt->n_events;
    buff[enc_len++] = tgt->n_events >> 8 & 0xff;
    buff[enc_len++] = tgt->n_events >> 16 & 0xff;
    buff[enc_len++] = tgt->n_events >> 24 & 0xff;
    // events
    for (i=0; i<tgt->n_events; i++) {
        // t
        buff[enc_len++] = tgt->t_events[i];
        buff[enc_len++] = tgt->t_events[i] >> 8 & 0xff;
        buff[enc_len++] = tgt->t_events[i] >> 16 & 0xff;
        buff[enc_len++] = tgt->t_events[i] >> 24 & 0xff;
        // val
        enc_p = (UI08*)&tgt->v_events[i];
        buff[enc_len++] = enc_p[0];
        buff[enc_len++] = enc_p[1];
        buff[enc_len++] = enc_p[2];
        buff[enc_len++] = enc_p[3];
    }
    // // sanity check
    // if (tgt->byte_size + sizeof(tgt->byte_size) != enc_len) {
    //     fprintf(stderr, "@FrameEncode: (enc_len = %llu)!= (tgt->byte_size + sizeof(tgt->byte_size) = %lu)!\n", enc_len, tgt->byte_size + sizeof(tgt->byte_size));
    //     exit(-1);
    // }
    // end
    return enc_len;
}

UI64
FrameDecode(
    Frame*                              tgt,
    const UI08*                         buff,
    const UI64                          buff_size
) {
    UI64 i, dec_len;
    UI08 *dec_p;

    if (buff_size < sizeof(tgt->byte_size)) {
        tgt->byte_size = 0;
        return 0;
    }

    dec_len = 0;
    // bytes size
    tgt->byte_size  = (UI32)buff[dec_len++]      ;
    tgt->byte_size += (UI32)buff[dec_len++] <<  8;
    tgt->byte_size += (UI32)buff[dec_len++] << 16;
    tgt->byte_size += (UI32)buff[dec_len++] << 24;

    if (buff_size < tgt->byte_size + sizeof(tgt->byte_size)) {
        return 0;
    }

    // frame_cnt
    tgt->frame_cnt  = (UI32)buff[dec_len++]      ;
    tgt->frame_cnt += (UI32)buff[dec_len++] <<  8;
    tgt->frame_cnt += (UI32)buff[dec_len++] << 16;
    tgt->frame_cnt += (UI32)buff[dec_len++] << 24;

    // io
    dec_len += VcdNodeVectorDecode(&tgt->fi, &buff[dec_len]);
    dec_len += VcdNodeVectorDecode(&tgt->fo, &buff[dec_len]);
    dec_len += VcdNodeVectorDecode(&tgt->tgt, &buff[dec_len]);

    // n_events
    tgt->n_events  = (UI32)buff[dec_len++];
    tgt->n_events += (UI32)buff[dec_len++] << 8;
    tgt->n_events += (UI32)buff[dec_len++] << 16;
    tgt->n_events += (UI32)buff[dec_len++] << 24;
    // events
    if (tgt->n_events >= tgt->a_events_) {
        tgt->t_events = (UI32*)realloc(
            tgt->t_events, tgt->n_events * sizeof(UI32)
        );
        if (!tgt->t_events) {
            fprintf(stderr, "@FrameDecode: Memory realloc failed!\n");
            exit(-1);
        }
        tgt->v_events = (FL32*)realloc(
            tgt->v_events, tgt->n_events * sizeof(FL32)
        );
        if (!tgt->v_events) {
            fprintf(stderr, "@FrameDecode: Memory realloc failed!\n");
            exit(-1);
        }
        tgt->a_events_ = tgt->n_events;
    }
    for (i = 0; i < tgt->n_events; i++) {
        // time
        tgt->t_events[i]  = (UI32)buff[dec_len++];
        tgt->t_events[i] += (UI32)buff[dec_len++] << 8;
        tgt->t_events[i] += (UI32)buff[dec_len++] << 16;
        tgt->t_events[i] += (UI32)buff[dec_len++] << 24;
        // value
        dec_p = (UI08*)&tgt->v_events[i];
        dec_p[0] = buff[dec_len++];
        dec_p[1] = buff[dec_len++];
        dec_p[2] = buff[dec_len++];
        dec_p[3] = buff[dec_len++];
    }
    // // sanity check
    // if (tgt->byte_size + sizeof(tgt->byte_size) != dec_len) {
    //     fprintf(stderr, "@FrameDecode: (dec_len = %llu) != (tgt->byte_size + sizeof(tgt->byte_size) = %lu)!\n", dec_len, tgt->byte_size + sizeof(tgt->byte_size));
    //     exit(-1);
    // }
    // end
    return dec_len;
}

UI64
FrameSize(
    Frame*                              tgt
) {
    tgt->byte_size = sizeof(tgt->frame_cnt);
    tgt->byte_size += VcdNodeVectorSize(&tgt->fi);
    tgt->byte_size += VcdNodeVectorSize(&tgt->fo);
    tgt->byte_size += VcdNodeVectorSize(&tgt->tgt);
    tgt->byte_size = sizeof(tgt->n_events);
    tgt->byte_size += tgt->n_events * 
        (sizeof(*tgt->t_events) + sizeof(*tgt->v_events));
    return (UI64)tgt->byte_size;
}
