"""MiSTer (TekWar, Witchaven): the 640-wide and 240-line modes laid out as
320x200. The core shows every mode on a 4:3 screen, and the engine's MiSTer
branch draws 2D art of a 320x200 screen with a column per xdim/320 pixels, so
the games' own "SVGA" layouts (made for 640x480) are wrong here: Witchaven
scaled its pictures to ydim/480, TekWar's end screens assumed 480 lines.
usage: patch_wide.py <jftekwar|jfwhaven>
"""
import os, sys

root = sys.argv[1]
CRLF = chr(13) + chr(10)

def edit(rel, pairs):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8', errors='replace', newline='').read()
    crlf = CRLF in s  # whmenu.c has CRLF line ends
    for old, new in pairs:
        if crlf:
            old, new = old.replace(chr(10), CRLF), new.replace(chr(10), CRLF)
        if new in s:
            continue
        assert s.count(old) == 1, f'{rel}: {old[:50]!r} x{s.count(old)}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patched', rel)

svga_old = '''    svga=!(xdim == 320 && ydim == 200) && !(xdim == 640 && ydim == 400);
'''
svga_new = '''#ifdef MISTER_HYBRID
    // MiSTer: every mode is a 320x200 screen to the game's 2D art (the
    // engine draws a column of it as xdim/320 pixels, the core shows 4:3)
    svga=0;
#else
    svga=!(xdim == 320 && ydim == 200) && !(xdim == 640 && ydim == 400);
#endif
'''
edit('src/whaven.c', [(svga_old, svga_new)])
edit('src/tekmsc.c', [('''     if( xdim == 640 ) {
          setview(0L,0L,xdim-1,ydim-1);
          loadtile(ES1A_SVGA);
''', '''#ifdef MISTER_HYBRID
     if( xdim == 640 && ydim >= 400 ) { // MiSTer: the SVGA pictures need 480 lines
#else
     if( xdim == 640 ) {
#endif
          setview(0L,0L,xdim-1,ydim-1);
          loadtile(ES1A_SVGA);
''')])
