// Corridor 8 on the MiSTer: the HMI Sound Operating System's digital sound
// and timer services the game's sound and timer modules call, on JonoF's
// jfaudiolib (the engine's sound), and the NetNow network and memcheck
// library calls as stubs. The game's own sound logic (corr7snd.c) is kept.
#include <stdio.h>
#include <string.h>
#include "sos.h"
#include "fx_man.h"
#include "compat.h"
#include "build.h"
#include "baselayer.h"

#define EMU_VOICES 32

static int digi_up;
_SOS_SYSTEM _sSOSSystem;
static struct {
    int voice;          // jfaudiolib voice handle, or 0
    _SOS_SAMPLE *sample;
} voices[EMU_VOICES];

static void voice_done(unsigned int callbackval) {
    int i = (int)callbackval;
    if (i >= 0 && i < EMU_VOICES) {
        voices[i].voice = 0;
        voices[i].sample = NULL;
    }
}

W32 sosDIGIInitSystem(PSTR szPath, W32 wFlags) { (void)szPath; (void)wFlags; _sSOSSystem.wFlags = _SOS_SYSTEM_INITIALIZED; return _ERR_NO_ERROR; }
W32 sosDIGIUnInitSystem(void) { return _ERR_NO_ERROR; }
W32 sosDIGIDetectInit(PSTR szPath) { (void)szPath; return _ERR_NO_ERROR; }
W32 sosDIGIDetectUnInit(void) { return _ERR_NO_ERROR; }
W32 sosDIGIDetectFindFirst(_SOS_DIGI_DRIVER *d) { (void)d; return _ERR_NO_ERROR; }
W32 sosDIGIDetectGetSettings(_SOS_DIGI_DRIVER *d) { (void)d; return _ERR_NO_ERROR; }
PSTR sosGetErrorString(W32 wError) { static char s[40]; snprintf(s, sizeof s, "SOS error %u", (unsigned)wError); return s; }

W32 sosDIGIInitDriver(_SOS_DIGI_DRIVER *d, W32 *hDriver) {
    int channels = 2, bits = 16, rate = d && d->wDriverRate ? (int)d->wDriverRate : 22050, err;
    if (!digi_up) {
        err = FX_Init(ASS_AutoDetect, EMU_VOICES, &channels, &bits, &rate, NULL);
        if (err != FX_Ok) {
            buildprintf("sosemu: FX_Init: %s\n", FX_ErrorString(err));
            return 1;
        }
        FX_SetCallBack(voice_done);
        FX_SetVolume(255);
        digi_up = 1;
        buildprintf("sosemu: sound up, %d Hz\n", rate);
    }
    if (d) { d->pfnMixFunction = NULL; d->wFlags |= _SOS_DRV_INITIALIZED; }
    *hDriver = 1;
    return _ERR_NO_ERROR;
}
W32 sosDIGIUnInitDriver(W32 hDriver, BOOL a, BOOL b) {
    (void)hDriver; (void)a; (void)b;
    if (digi_up) { FX_Shutdown(); digi_up = 0; }
    return _ERR_NO_ERROR;
}

// SOS volumes are 0..0x7fff a channel, packed; jfaudiolib's are 0..255
static int vol255(W32 packed) {
    W32 l = packed >> 16, r = packed & 0xffff;
    W32 v = l > r ? l : r;
    if (v > 0x7fff) v = 0x7fff;
    return (int)(v >> 7);
}
static int pan255(W32 pan, int right) {
    // 0 = left, 0x8000 = centre, 0xffff = right
    int p = (int)(pan >> 8); // 0..255
    return right ? p : 255 - p;
}

W32 sosDIGIStartSample(W32 hDriver, _SOS_SAMPLE *s) {
    int i, v, vol, l, r;
    (void)hDriver;
    if (!digi_up || !s || !s->pSample || !s->wLength) return (W32)-1;
    for (i = 0; i < EMU_VOICES; i++) if (!voices[i].voice) break;
    if (i == EMU_VOICES) return (W32)-1;
    vol = vol255(s->wVolume);
    l = pan255(s->wPanPosition, 0) * vol / 255;
    r = pan255(s->wPanPosition, 1) * vol / 255;
    // the data is raw PCM (the WAV header was stepped over by the game)
    if (s->wLoopCount) {
        v = FX_PlayLoopedRaw((char *)s->pSample, (int)s->wLength, (char *)s->pSample, (char *)s->pSample + s->wLength, (int)s->wRate, 0, vol, l, r, (int)s->wPriority, (unsigned int)i);
    } else {
        v = FX_PlayRaw((char *)s->pSample, (int)s->wLength, (int)s->wRate, 0, vol, l, r, (int)s->wPriority, (unsigned int)i);
    }
    if (v < FX_Ok) return (W32)-1;
    voices[i].voice = v;
    voices[i].sample = s;
    s->hSample = (W32)i;
    return (W32)i;
}
W32 sosDIGIStopSample(W32 hDriver, W32 hSample) {
    (void)hDriver;
    if (hSample < EMU_VOICES && voices[hSample].voice) {
        FX_StopSound(voices[hSample].voice);
        voices[hSample].voice = 0;
        voices[hSample].sample = NULL;
    }
    return _ERR_NO_ERROR;
}
BOOL sosDIGISampleDone(W32 hDriver, W32 hSample) {
    (void)hDriver;
    if (hSample >= EMU_VOICES || !voices[hSample].voice) return _TRUE;
    if (!FX_SoundActive(voices[hSample].voice)) { voices[hSample].voice = 0; voices[hSample].sample = NULL; return _TRUE; }
    return _FALSE;
}
W32 sosDIGISetSampleVolume(W32 hDriver, W32 hSample, W32 wVolume) {
    (void)hDriver;
    if (hSample < EMU_VOICES && voices[hSample].voice) {
        _SOS_SAMPLE *s = voices[hSample].sample;
        int vol = vol255(wVolume), pan = s ? (int)s->wPanPosition : _PAN_CENTER;
        if (s) s->wVolume = wVolume;
        FX_SetPan(voices[hSample].voice, vol, pan255(pan, 0) * vol / 255, pan255(pan, 1) * vol / 255);
    }
    return _ERR_NO_ERROR;
}
W32 sosDIGISetPanLocation(W32 hDriver, W32 hSample, W32 wPan) {
    (void)hDriver;
    if (hSample < EMU_VOICES && voices[hSample].voice) {
        _SOS_SAMPLE *s = voices[hSample].sample;
        int vol = s ? vol255(s->wVolume) : 255;
        if (s) s->wPanPosition = wPan;
        FX_SetPan(voices[hSample].voice, vol, pan255(wPan, 0) * vol / 255, pan255(wPan, 1) * vol / 255);
    }
    return _ERR_NO_ERROR;
}
W32 sosDIGIGetSampleHandle(W32 hDriver, W32 wID) {
    int i;
    (void)hDriver;
    for (i = 0; i < EMU_VOICES; i++) {
        if (voices[i].voice && voices[i].sample && voices[i].sample->wID == wID) {
            if (!FX_SoundActive(voices[i].voice)) { voices[i].voice = 0; voices[i].sample = NULL; continue; }
            return (W32)i;
        }
    }
    return (W32)-1;
}
W32 sosDIGIGetSampleID(W32 hDriver, W32 hSample) {
    (void)hDriver;
    if (hSample < EMU_VOICES && voices[hSample].voice && voices[hSample].sample) return voices[hSample].sample->wID;
    return (W32)-1;
}

// Timer events: the game registers handlers with a rate; the engine's timer
// callback (120 Hz) runs sosemu_tick(), which calls each at its rate
#define EMU_EVENTS 8
static struct { VOID (*fn)(VOID); W32 rate; W32 acc; } events[EMU_EVENTS];
W32 sosTIMERInitSystem(W32 wRate, W32 wFlags) { (void)wRate; (void)wFlags; return _ERR_NO_ERROR; }
W32 sosTIMERUnInitSystem(W32 wFlags) { (void)wFlags; memset(events, 0, sizeof events); return _ERR_NO_ERROR; }
W32 sosTIMERRegisterEvent(W32 wRate, VOID (*pfn)(VOID), W32 *hEvent) {
    int i;
    if (!pfn) { *hEvent = (W32)-1; return _ERR_NO_ERROR; }
    for (i = 0; i < EMU_EVENTS; i++) if (!events[i].fn) break;
    if (i == EMU_EVENTS) { *hEvent = (W32)-1; return 1; }
    events[i].fn = pfn; events[i].rate = wRate ? wRate : 120; events[i].acc = 0;
    *hEvent = (W32)i;
    return _ERR_NO_ERROR;
}
W32 sosTIMERRemoveEvent(W32 hEvent) {
    if (hEvent < EMU_EVENTS) events[hEvent].fn = NULL;
    return _ERR_NO_ERROR;
}
void sosemu_tick(void) {
    int i;
    for (i = 0; i < EMU_EVENTS; i++) {
        if (!events[i].fn) continue;
        events[i].acc += events[i].rate;
        while (events[i].acc >= 120) {
            events[i].acc -= 120;
            events[i].fn();
        }
    }
}
BOOL sosEZGetConfig(PSTR szName) { (void)szName; return _FALSE; }

// NetNow: no network
W32 hmiNETNOWInitSystem(W32 w) { (void)w; return _NETNOW_NO_NETWORK; }
W32 hmiNETNOWUnInitSystem(void) { return 0; }
W32 hmiNETNOWPostListen(void) { return 0; }
W32 hmiNETNOWGetNetworkAddr(_NETNOW_NODE_ADDR *a) { if (a) memset(a, 0, sizeof *a); return 0; }
W32 hmiNETNOWGetConsoleNode(void) { return 0; }
W32 hmiNETNOWGetActiveNodes(void) { return 1; }
W32 hmiNETNOWSendData(PSTR hdr, W32 hdrlen, PSTR data, W32 len, W32 node) { (void)hdr; (void)hdrlen; (void)data; (void)len; (void)node; return 1; }
W32 hmiNETNOWGetHeader(PSTR hdr, W32 hdrlen, void *packet) { (void)hdr; (void)hdrlen; (void)packet; return 1; }
W32 hmiNETNOWGetBlock(void *packet, PSTR data, W32 len) { (void)packet; (void)data; (void)len; return 1; }
W32 hmiNETNOWAddNode(_NETNOW_NODE_ADDR *a) { (void)a; return 0; }
W32 hmiNETNOWDeleteNode(W32 node) { (void)node; return 0; }
W32 hmiNETNOWSortNodes(void) { return 0; }

int mc_is_active(void) { return 0; }
long mc_bytes_allocated(void) { return 0; }
