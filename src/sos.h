/* Corridor 8 on the MiSTer: a stand-in for the HMI Sound Operating System,
   NetNow and Smacker headers the DOS game included. The types and constants
   its modules use; the functions are in sosemu.c (on JonoF's jfaudiolib). */
#ifndef C8_SOS_SHIM_H
#define C8_SOS_SHIM_H
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#ifndef O_BINARY
#define O_BINARY 0
#endif
#ifndef S_IREAD
#define S_IREAD S_IRUSR
#define S_IWRITE S_IWUSR
#endif
#define stricmp strcasecmp
#define strcmpi strcasecmp
#define cdecl
#define __cdecl
#define far
#define near
#define _far
#define _loadds
#define __pascal
#define RCFUNC
#define RADLINK
#define PTR4
typedef unsigned short WORD;
typedef unsigned char BYTE;
typedef unsigned int DWORD;
typedef unsigned int W32;
typedef unsigned short W16;
typedef unsigned char W8;
typedef unsigned int u32;
typedef char *PSTR;
typedef void *LPSTR;
typedef void VOID;
typedef int BOOL;
typedef W32 HANDLE;
#define _TRUE 1
#define _FALSE 0
#define _NULL NULL
#ifndef _MAX_PATH
#define _MAX_PATH 260
#define _MAX_FNAME 256
#define _MAX_EXT 256
#endif

/* SOS: errors, flags */
#define _ERR_NO_ERROR 0
#define _SOS_DEBUG_NORMAL 0
#define _TIMER_DOS_RATE 0
#define _PCM_UNSIGNED 0x80
#define _PAN_CENTER 0x8000
#define _PAN_LEFT 0x0000
#define _PAN_RIGHT 0xffff
#define MK_VOLUME(l, r) ((W32)((W32)(l) << 16 | (W32)(r)))
#define _SOS_MAX_VOLUME 0x7fff

typedef struct _SOS_SAMPLE {
    PSTR pSample;
    W32 wLength;
    W32 wRate;
    W32 wBitsPerSample;
    W32 wChannels;
    W32 wFormat;
    W32 wVolume;
    W32 wPanPosition;
    W32 wLoopCount;
    W32 wID;
    W32 wPriority;
    W32 hSample;
    VOID *pfnSampleDone;
    W32 wSampleRate;
    PSTR pSampleStart;
} _SOS_SAMPLE;

typedef struct _SOS_DIGI_DRIVER {
    W32 wDriverRate;
    W32 wDriverFormat;
    W32 wDMABufferSize;
    W32 wFlags;
    W32 wPort, wDMA, wIRQ, wParam, wID;
    VOID (*pfnMixFunction)(VOID);
} _SOS_DIGI_DRIVER;
typedef struct { W32 wPort, wDMA, wIRQ, wParam, wID, wTimerID; } _SOS_HARDWARE;
typedef struct { W32 wPort, wDMA, wIRQ, wID, wTimerID; } _SOS_MIDI_HARDWARE;
typedef struct { W32 wFlags; } _SOS_SYSTEM;
extern _SOS_SYSTEM _sSOSSystem;
#define _SOS_SYSTEM_INITIALIZED 1
#define _SOS_DRV_INITIALIZED 1
#define _DRV_SWAP_CHANNELS 0
typedef struct { W32 wCaps; char szDeviceName[32]; } _SOS_CAPABILITIES;


/* the SOS functions the game calls (sosemu.c) */
W32 sosDIGIInitSystem(PSTR szPath, W32 wFlags);
W32 sosDIGIUnInitSystem(void);
W32 sosDIGIDetectInit(PSTR szPath);
W32 sosDIGIDetectUnInit(void);
W32 sosDIGIDetectFindFirst(_SOS_DIGI_DRIVER *d);
W32 sosDIGIDetectGetSettings(_SOS_DIGI_DRIVER *d);
W32 sosDIGIInitDriver(_SOS_DIGI_DRIVER *d, W32 *hDriver);
W32 sosDIGIUnInitDriver(W32 hDriver, BOOL a, BOOL b);
W32 sosDIGIStartSample(W32 hDriver, _SOS_SAMPLE *s);
W32 sosDIGIStopSample(W32 hDriver, W32 hSample);
BOOL sosDIGISampleDone(W32 hDriver, W32 hSample);
W32 sosDIGISetSampleVolume(W32 hDriver, W32 hSample, W32 wVolume);
W32 sosDIGISetPanLocation(W32 hDriver, W32 hSample, W32 wPan);
W32 sosDIGIGetSampleHandle(W32 hDriver, W32 wID);
W32 sosDIGIGetSampleID(W32 hDriver, W32 hSample);
PSTR sosGetErrorString(W32 wError);
W32 sosTIMERInitSystem(W32 wRate, W32 wFlags);
W32 sosTIMERUnInitSystem(W32 wFlags);
W32 sosTIMERRegisterEvent(W32 wRate, VOID (*pfn)(VOID), W32 *hEvent);
W32 sosTIMERRemoveEvent(W32 hEvent);
BOOL sosEZGetConfig(PSTR szName);
void sosemu_tick(void);   /* the engine's timer callback: the registered events */

/* NetNow (no network on the MiSTer: every call reports no network) */
#define _NETNOW_NO_ERROR 0
#define _NETNOW_NO_NETWORK 1
#define _NETNOW_MAX_LISTEN_PACKETS 8
typedef struct _NETNOW_NODE_ADDR { W8 addr[10]; } _NETNOW_NODE_ADDR;
typedef struct _XFER_BLOCK_HEADER { W32 wType; W32 wNode; W32 wLength; } _XFER_BLOCK_HEADER;
#define _XFER_BLOCK_DATA 0
#define _NETNOW_BROADCAST 0xffff
W32 hmiNETNOWInitSystem(W32 w);
W32 hmiNETNOWUnInitSystem(void);
W32 hmiNETNOWPostListen(void);
W32 hmiNETNOWGetNetworkAddr(_NETNOW_NODE_ADDR *a);
W32 hmiNETNOWGetConsoleNode(void);
W32 hmiNETNOWGetActiveNodes(void);
W32 hmiNETNOWSendData(PSTR hdr, W32 hdrlen, PSTR data, W32 len, W32 node);
W32 hmiNETNOWGetHeader(PSTR hdr, W32 hdrlen, void *packet);
W32 hmiNETNOWGetBlock(void *packet, PSTR data, W32 len);
W32 hmiNETNOWAddNode(_NETNOW_NODE_ADDR *a);
W32 hmiNETNOWDeleteNode(W32 node);
W32 hmiNETNOWSortNodes(void);

/* Smacker (the game's player is switched off) */
typedef struct { int Frames; int NewPalette; char Palette[768]; } Smack;

/* the DOS text screen (Watcom graph.h): nothing */
#define _TEXTC80 0
#define _GWINDOW 0
#define _GCURSORON 0
#define _GCURSOROFF 0
#define _setvideomode(m) ((void)0)
#define _setbkcolor(c) ((void)0)
#define _settextcolor(c) ((void)0)
#define _gettextcolor() 0
#define _settextwindow(a,b,c,d) ((void)0)
#define _clearscreen(a) ((void)0)
#define _outtext(t) ((void)0)
#define _displaycursor(c) ((void)0)
#define _settextposition(a,b) ((void)0)
/* memcheck (a DOS debug library) */
int mc_is_active(void);
long mc_bytes_allocated(void);
#endif
