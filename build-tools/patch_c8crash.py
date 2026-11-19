"""Corridor 8 (2026-11-18): a crash reporter. The MiSTer's kernel writes no
core file and the -O0 build under gdb behaved differently from the release,
so the release reports itself: on SIGSEGV / SIGBUS / SIGILL / SIGFPE / SIGABRT
the game prints the signal and a raw backtrace (addresses) to its log, then
dies with the signal as before. Symbolize with
arm-linux-gnueabihf-addr2line -f -C -e build/jfcorr8 <addr>... (non-PIE).
Build with -funwind-tables -fno-omit-frame-pointer (q_c8full.sh) so the
unwinder gets past the first frame.
usage: patch_c8crash.py <jfcorr8 tree>  (idempotent)"""
import os, sys
root = sys.argv[1]

def edit(rel, pairs):
    p = os.path.join(root, rel); s = open(p, encoding='utf-8', errors='replace', newline='').read(); crlf = '\r\n' in s
    for old, new in pairs:
        if crlf: old, new = old.replace('\n', '\r\n'), new.replace('\n', '\r\n')
        if new in s: continue
        assert s.count(old) == 1, f'{rel}: {old[:60]!r} x{s.count(old)}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8', newline='').write(s); print('patched', rel)

edit('src/c8port.c', [
    ('''void c8_misterinit(void) { }
''', '''void c8_misterinit(void) { }

// A crash reports itself to the log (the MiSTer writes no core file):
// the signal and the raw backtrace, to symbolize with addr2line against
// the unstripped build (non-PIE, so the addresses are the binary's).
#include <signal.h>
#include <execinfo.h>
#include <unistd.h>
static void c8_crashreport(int sig) {
    void *frames[40];
    char line[64];
    int n = backtrace(frames, 40), i, len;
    len = snprintf(line, sizeof line, "c8 crash: signal %d, backtrace:\\n", sig);
    write(1, line, len);
    for (i = 0; i < n; i++) {
        len = snprintf(line, sizeof line, "  %p\\n", frames[i]);
        write(1, line, len);
    }
    signal(sig, SIG_DFL);
    raise(sig);
}
__attribute__((constructor)) static void c8_crashreport_init(void) {
    signal(SIGSEGV, c8_crashreport);
    signal(SIGBUS, c8_crashreport);
    signal(SIGILL, c8_crashreport);
    signal(SIGFPE, c8_crashreport);
    signal(SIGABRT, c8_crashreport);
}
'''),
])
print('c8 crash reporter OK')
