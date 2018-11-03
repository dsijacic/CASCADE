/* main.c -- created by DS. */

#include <time.h>
#include "defs.h"
#include "vcd2pff.h"
#include "pff_wr.h"

#define VERSION 0xbeef

void help(FILE* out) {
    fprintf(out, "-----------------------------------------------------------------------------\n");
    fprintf(out, " vcd2pff  <*.vcd>  <*.iox> <*.pff> [-psfdutNz <val>] [-u]\n");
    fprintf(out, "  -p :  frame period           (uint32)\n");
    fprintf(out, "  -s :  start sample           (uint64)\n");
    fprintf(out, "  -f :  finish sample          (uint64)\n");
    fprintf(out, "  -d :  0.0 <= d <= 1.0        (float)\n");
    fprintf(out, "  -u :  use trigger            (flag)\n");
    fprintf(out, "  -t :  trigger name           (string)\n");
    fprintf(out, "  -N :  note                   (string)\n");
    fprintf(out, "  -z :  hierSeparator          (char)\n");
    fprintf(out, "  -h :  display help an exit   (flag)\n");
;
}
int main(int argc, CHAR** argv) {
    /* timer */
    clock_t                 tStart, tEnd;
    UI64                    eta, hrs, min, sec, msec;

    /* Command line interface */
    
    UI32                    period = 0;
    UI64                    start = 0;
    UI32                    nFrames = 0;
    UI64                    finish = 0;
    FL32                    switchingDistance = 0.0;
    CHAR                    hierSeparator = '/';
    FLAG                    useTrigger = 0;

    if (argc < 4) {
        help(stderr);
        return ERR_ARGS;
    }

    CHAR*                   vcdFile = argv[1];
    CHAR*                   ioxFile = argv[2];
    CHAR*                   pffFile = argv[3];
    CHAR*                   note = 0;
    CHAR*                   trigger = 0;

    ERR_CODE returnCode = ERR_SUCCESS;

    UI08 argp = 4;

    while (argp < argc) {
        if (argv[argp][0] == '-') {
            switch (argv[argp++][1]) {
            case 'p':
                period = strtoul(argv[argp], 0, 0);
                break;
            case 's':
                start = strtoull(argv[argp], 0, 0);
                break;
            case 'f':
                finish = strtoull(argv[argp], 0, 0);
                break;
            case 'n':
                nFrames = strtoul(argv[argp], 0, 0);
                break;
            case 'd':
                switchingDistance = atof(argv[argp]);
                break;
            case 'N':
                note = argv[argp];
                break;
            case 'u':
                useTrigger = 1;
                argp--;
                break;
            case 't':
                trigger = argv[argp];
                break;
            case 'z':
                hierSeparator = argv[argp][0];
                break;
            case 'h':
                help(stdout);
                returnCode = ERR_SUCCESS;
                break;
            default:
                fprintf(stderr, "\t+ Invalid argument %s.\n", argv[argp-1]);
                returnCode = ERR_ARGS;
                break;
            }
            argp++;
        } else {
            fprintf(stderr, 
                "\t+ Invalid argument %s! Expected one of - arguments.\n", 
                argv[argp]);
            returnCode = ERR_ARGS;
            break;
        }
    }

    if (returnCode != ERR_SUCCESS) return returnCode;
    if (period == 0) {
        fprintf(stderr, "\t+ Period must be a positive integer!\n");
        return ERR_ARGS;
    }
    if (start == 0) 
        start = period;

    if (useTrigger && !trigger) {
        fprintf(stderr, "\t+ Must specify trigger name!\n");
        return ERR_ARGS;
    }

    fprintf(stdout, "Starting VCD to PFF conversion.\n");

    PowerFrameFile  pff;
    Frame           frame;
    VcdNodeVector   exclude;
    VcdNode         triggerNode;
    FLAG            triggerFound;

    VcdNode*        allNodes;
    FL32            resolution;
    UI64            vcdLineCnt;
    FILE*           vcdFp;
    FILE*           ioxFp;

    tStart = clock();

    returnCode = Vcd2PffSetup(
        vcdFile,
        ioxFile,
        &frame,
        &exclude,
        hierSeparator,
        useTrigger,
        trigger,
        &triggerNode,
        &triggerFound,
        &vcdFp,
        &ioxFp,
        &vcdLineCnt,
        &resolution,
        &allNodes
    );

    if (returnCode == ERR_SUCCESS)
        returnCode = PffWriterInit(
            &pff, 
            VERSION,
            note, 
            resolution, 
            period, 
            frame.fi.width, 
            frame.fo.width, 
            frame.tgt.width
        );

    if (returnCode == ERR_SUCCESS)
        returnCode = PffWriterOpen(&pff, pffFile);
    if (returnCode == ERR_SUCCESS)
        returnCode = Vcd2PffRun(
            &pff, 
            &vcdFp, 
            &frame, 
            &allNodes, 
            &exclude,
            &triggerNode, 
            useTrigger,
            &start,
            &finish,
            &vcdLineCnt,
            period,
            switchingDistance
        );
    FrameKill(&frame);
    PffWriterClose(&pff);
    PffWriterKill(&pff);
    Vcd2PffFinish(&vcdFp, vcdLineCnt, &ioxFp, &allNodes);

    tEnd = clock();

    if (returnCode == ERR_SUCCESS)
        printf("\t+ VCD to PFF conversion completed succesfully.\n");
    else
        printf("\t+ VCD to PFF conversion failed.\n");

    /* ETA */
    eta = (tEnd - tStart) * 1000 / CLOCKS_PER_SEC;
    msec = eta % 1000;
    sec = eta / 1000;
    min = sec / 60;
    sec = sec % 60;
    hrs = min / 60;
    min = min % 60;

    printf("Elapsed time: %lluh:%02llum:%02llus:%03llums\n", 
        hrs, min, sec, msec);

    return returnCode;
}