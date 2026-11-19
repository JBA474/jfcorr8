"""Corridor 8 (2026-11-18): the crash in the menus and in play, caught by the
crash reporter: PLR_useCheck() (the use key, which is also the pad's A /
menu OK, and the game keeps running its frame behind the options menus)
calls EFF_operatableSector(nearsector) with nearsector == -1 when nothing
is near, and that reads sectorPtr[-1]: harmless garbage on DOS, a segfault
here (exit code 139 on entering Controller Options, after flipping through
the menus, when starting a campaign). The use check skips -1, and the
sector test refuses any sector number outside the map.
usage: patch_c8use.py <jfcorr8 tree>  (idempotent)"""
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

edit('src/corr7plr.c', [
    ('''     if (!EFF_operatableSector(nearsector)) {
          if (EFF_operatableSector(sector)) {
               nearsector=sector;
          }
     }
''', '''     // nothing near (-1) is not a sector: the DOS game read sectorPtr[-1]
     // and got away with it, the port crashed (MiSTer, 2026-11-18)
     if (nearsector == -1 || !EFF_operatableSector(nearsector)) {
          if (sector != -1 && EFF_operatableSector(sector)) {
               nearsector=sector;
          }
     }
'''),
])
edit('src/corr7eff.c', [
    ('''EFF_operatableSector(short s)
{
     if (EFF_isDoor(s) || EFF_isElevator(s)) {
''', '''EFF_operatableSector(short s)
{
     if (s < 0 || s >= numsectors) {   // -1 from neartag(): not a sector (MiSTer)
          return(0);
     }
     if (EFF_isDoor(s) || EFF_isElevator(s)) {
'''),
])
print('c8 use check OK')
