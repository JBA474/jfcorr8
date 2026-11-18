"""Corridor 8: Galactic Wars on JonoF's jfbuild (the MiSTer branch): the DOS
parts of the game modules replaced. Applied to fresh copies of the sources
by q_c8full.sh; idempotent. usage: port_c8.py <jfcorr8 tree>"""
import os, re, sys

tree = sys.argv[1]
SRC = os.path.join(tree, 'src')
NL = chr(10)

def load(name):
    return open(os.path.join(SRC, name), encoding='latin1', newline='').read().replace(chr(13) + NL, NL)

def save(name, s):
    open(os.path.join(SRC, name), 'w', encoding='latin1', newline=NL).write(s)

def sub1(s, pattern, repl, flags=0, count=1):
    return re.sub(pattern, repl, s, count=count, flags=flags)

def add_last_arg(s, fname, extra):
    """Append `, extra` to every call of fname(...) (parentheses matched)."""
    out, i = [], 0
    pat = re.compile(r'(?<![A-Za-z_0-9])' + re.escape(fname) + r'\s*\(')
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); break
        depth, j = 0, m.end() - 1
        while j < len(s):
            if s[j] == '(': depth += 1
            elif s[j] == ')':
                depth -= 1
                if depth == 0: break
            j += 1
        inner = s[m.end():j]
        if inner.rstrip().endswith(extra):
            out.append(s[i:j + 1])
        else:
            out.append(s[i:m.end()] + inner + ', ' + extra + ')')
        i = j + 1
    return ''.join(out)

# ---------------------------------------------------------------- corr7.h
s = load('corr7.h')
m = re.search(r'//\*\*\n//\*\* Prototypes for BUILD functions\n//\*\*\n', s)
if m:
    rest = s[m.end():]
    m2 = re.search(r'\n//\*\*', rest)
    end = m.end() + (m2.start() if m2 else len(rest))
    s = s[:m.start()] + '// (the BUILD prototypes of the DOS engine: build.h has the port' + "'" + 's)\n' + s[end:]
# engine globals the DOS header declared itself
s = re.sub(r'(?m)^extern(?:\s+volatile)?\s*\n(?:volatile\s+)?(?:char|short|int|unsigned char)\s+(scantoasc|scantoascwithshift|keystatus|totalclock|numframes|xdim|ydim|randomseed|numsectors|numwalls|palette|transluc|tempbuf|names)\s*(\[[^\]]*\])*\s*;\s*\n', '', s)
s = re.sub(r'(?m)^extern(?:\s+volatile)?\s+(?:volatile\s+)?(?:char|short|int|unsigned char)\s+(scantoasc|scantoascwithshift|keystatus|totalclock|numframes|xdim|ydim|randomseed|numsectors|numwalls|palette|transluc|tempbuf|names)\s*(\[[^\]]*\])*\s*;\s*\n', '', s)
# the editor's screen functions: the port declares its own stubs (c8port.h)
s = re.sub(r'(?m)^[^\n]*\b(getnumber16|printmessage16|clearmidstatbar16|gettile|draw2dscreen|clear2dscreen|printext16|editinput|drawline16|keytimerstuff)\s*\([^;]*;\s*\n', '', s)
# the structs the prototype files name before they are defined
if 'struct menuOption;' not in s:
    s = 'struct menuOption;\nstruct doorData;\n' + s
save('corr7.h', s)

# ---------------------------------------------------------------- the .def prototypes
for name in [f for f in os.listdir(SRC) if f.endswith('.def')]:
    s = load(name)
    s = s.replace('extern void ExtInit(void );', 'extern int ExtInit(void );')
    s = re.sub(r'(?m)^extern void (inittimer|uninittimer)\(void \);\n', '', s)
    s = re.sub(r'(?m)^extern void (initkeys|uninitkeys)\(void \);\n', '', s)
    s = re.sub(r'(?m)^[^\n]*\b(getnumber16|printmessage16|clearmidstatbar16|gettile|draw2dscreen|clear2dscreen|printext16|editinput|drawline16|keytimerstuff)\s*\([^;]*;\s*\n', '', s)
    save(name, s)

# ---------------------------------------------------------------- icorp.h
s = load('icorp.h')
if 'baselayer.h' not in s:
    s = s.replace('#include "build.h"', '#include "build.h"\n#include "baselayer.h"\n#include "cache1d.h"\n#include "pragmas.h"\n#include "mmulti.h"\n#include <unistd.h>')
if 'c8port.h' not in s:
    s = s.rstrip(NL) + '\n#include "c8port.h"\n'
save('icorp.h', s)

# ---------------------------------------------------------------- corr7.c
s = load('corr7.c')
s = sub1(s, r'void\ninitVid\(void\)\n\{.*?\n\}\n', 'void\ninitVid(void)\n{\n}\n', flags=re.S)
s = re.sub(r'(?m)^[ \t]*_settextposition\([^;]*\);[ \t]*\n', '', s)
s = re.sub(r'(?m)^[ \t]*(initkeys|uninitkeys|uninittimer)\(\);[ \t]*\n', '', s)
if 'uninitengine();' not in s:
    s = s.replace('     uninitgroupfile();\n', '     uninitgroupfile();\n     uninitengine();\n', 1)
s = s.replace('strcpy(&mapFileName,argv[i+1]);', 'strcpy(mapFileName,argv[i+1]);')
s = s.replace('vsprintf(&debugstr[debugline],fmt,argptr);', 'vsprintf(debugstr[debugline],fmt,argptr);')
s = s.replace('printext256(debugx[i],debugy[i],P256COLOR,-1,&debugstr[i],1);', 'printext256(debugx[i],debugy[i],P256COLOR,-1,debugstr[i],1);')
save('corr7.c', s)

# ---------------------------------------------------------------- corr7eng.c
s = load('corr7eng.c')
s = s.replace('initengine(videoMode,videoResX,videoResY);', 'if (initengine()) crash("initengine: %s", engineerrstr);')
s = s.replace('loadpics("tiles000.art");', 'loadpics("tiles000.art", 8*1048576);')
s = re.sub(r'(?m)^[ \t]*setvmode\(0x03\);[ \t]*\n', '', s)
s = re.sub(r'(?m)^[ \t]*outp\(0x3c[89],[^;]*\);[^\n]*\n', '', s)
s = re.sub(r'(?<![A-Za-z_])setgamemode\(\)', 'c8_setgamemode()', s)
s = re.sub(r'(?<![A-Za-z_])qsetmode640480\(\)', 'c8_setgamemode()', s)
# the game's inittimer()/uninittimer() clash with the engine's: the timer module is called directly
s = sub1(s, r'void[ \t]*(//[^\n]*)?\ninittimer\(void\)\n\{\n[ \t]*TMR_initTimer\(\);\n\}\n', '', flags=re.S)
s = sub1(s, r'void[ \t]*(//[^\n]*)?\nuninittimer\(void\)\n\{\n[ \t]*TMR_uninitTimer\(\);\n\}\n', '', flags=re.S)
s = re.sub(r'(?m)^([ \t]*)inittimer\(\);', r'\1TMR_initTimer();', s)
s = re.sub(r'(?m)^[ \t]*initkeys\(\);[^\n]*\n', '', s)
# the game is started from ExtInit (the port's app_main calls it)
s = s.replace('void\nExtInit(void)', 'int\nExtInit(void)')
s = sub1(s, r'(int\nExtInit\(void\)\n\{.*?)(\n\})', r'\1\n     return 0;\2', flags=re.S)
s = re.sub(r'(?<![A-Za-z_0-9])loadboard\(', 'c8_loadboard(', s)
save('corr7eng.c', s)

ALLOC = r'allocache\(&\(?([A-Za-z_0-9]+(?:\[[^\]]*\])*(?:(?:\.|->)[A-Za-z_0-9]+(?:\[[^\]]*\])*)*)\)?,'
for name in ('corr7eng.c', 'corr7men.c', 'corr7eff.c', 'corr7act.c', 'corr7plr.c', 'corr7gam.c', 'corr7smk.c', 'corr7snd.c', 'corr7wep.c', 'corr7mul.c'):
    s = load(name)
    s = re.sub(ALLOC, r'allocache((void **)&\1,', s)
    save(name, s)

# ---------------------------------------------------------------- corr7gam.c
s = load('corr7gam.c')
s = re.sub(r'(?<![A-Za-z_0-9])loadboard\(', 'c8_loadboard(', s)
save('corr7gam.c', s)

# ---------------------------------------------------------------- corr7plr.c / corr7wep.c
s = load('corr7plr.c')
s = s.replace('setbrightness(gammaCorrection,(char *)&palette[0]);', 'setbrightness(gammaCorrection,palette,0);')
save('corr7plr.c', s)
s = load('corr7wep.c')
s = add_last_arg(s, 'hitscan', 'CLIPMASK1')
# rumble: the player's weapon going off
s = s.replace('''WEP_shootWeapon(short owner,int z,int hor,''', '''WEP_shootWeapon(short owner,int z,int hor,''', 1)
m = re.search(r'WEP_shootWeapon\(short owner,int z,int hor,[^{]*\{\n', s)
if m and 'misterrumble(0, 150, 110)' not in s:
    s = s[:m.end()] + '#ifdef MISTER_HYBRID\n     if (owner == PLR_getPlayerSprite(myconnectindex)) {\n          misterrumble(0, 150, 110); // MiSTer: the weapon\n     }\n#endif\n' + s[m.end():]
# the tile names file is read at startup: a missing one crashed in fclose(NULL)
s = s.replace('     fp=fopen("names.h","rt");\n', '     fp=fopen("names.h","rt");\n     if (fp == NULL) {\n          crash("names.h (the tile names, from the game\'s folder) was not found");\n     }\n', 1)
save('corr7wep.c', s)

# ---------------------------------------------------------------- corr7men.c: char arrays named as char *
s = load('corr7men.c')
s = re.sub(r'&(actionName|saveGameName)\[', r'\1[', s)
save('corr7men.c', s)
# ---------------------------------------------------------------- corr7mul.c / corr7plr.c: engine calls with short arguments
s = load('corr7mul.c')
s = re.sub(r'(?<![A-Za-z_0-9])getpacket\(', 'c8_getpacket(', s)
save('corr7mul.c', s)
s = load('corr7plr.c')
s = re.sub(r'(?<![A-Za-z_0-9])getmousevalues\(', 'c8_getmousevalues(', s)
save('corr7plr.c', s)

# ---------------------------------------------------------------- corr7act.c: rumble when the player is hurt
s = load('corr7act.c')
m = re.search(r'ACT_damageActor\(short s,int d,int useskill\)\n\{\n', s)
if m and 'MiSTer: hit' not in s:
    s = s[:m.end()] + '#ifdef MISTER_HYBRID\n     if (s == PLR_getPlayerSprite(myconnectindex) && d > 0) { // MiSTer: hit; harder for a bigger one\n          int strong = 80 + d * 2;\n          misterrumble(strong > 255 ? 255 : strong, 60, 220);\n     }\n#endif\n' + s[m.end():]
save('corr7act.c', s)

# ---------------------------------------------------------------- corr7eng.c: the prototype's debug line only when asked
s = load('corr7eng.c')
s = s.replace('     debugOutput();\n', '     if (getenv("C8DEBUG")) debugOutput();\n', 1)
save('corr7eng.c', s)

# ---------------------------------------------------------------- corr7gfx.c
s = load('corr7gfx.c')
s = re.sub(r'extern void near asmwaitvrt\(int p\);\n#pragma aux asmwaitvrt.*?modify \[eax edx\];\n', '', s, flags=re.S)
s = re.sub(r'extern void near asmsetpalette\(char \*p\);\n#pragma aux asmsetpalette.*?modify \[eax ecx edx\];\n', '', s, flags=re.S)
s = s.replace('     asmwaitvrt(1);\n     asmsetpalette(pal);', '     setbrightness(0, (unsigned char *)pal, 0); // the port: the engine\'s palette')
s = re.sub(r'GFX_setPalette\(&(redPal|greenPal|bluePal)\[([^\]]+)\]\)', r'GFX_setPalette((char *)\1[\2])', s)
save('corr7gfx.c', s)

# ---------------------------------------------------------------- corr7kbd.c / corr7gfx.c: the wait loops poll the keys;
# the engine's events (and with them its timer tick) are pumped there
s = load('corr7kbd.c')
s = s.replace('KBD_keyPressed(void)\n{\n     int  k;\n     static int lastMouseB;\n', 'KBD_keyPressed(void)\n{\n     int  k;\n     static int lastMouseB;\n     handleevents();               // the port: the DOS game had interrupts\n', 1)
save('corr7kbd.c', s)
s = load('corr7gfx.c')
s = s.replace('     KBD_resetKeys();\n     do {\n          if (fadeOutFlag) {', '     KBD_resetKeys();\n     do {\n          handleevents();          // the port: the timer tick that moves the fade\n          if (fadeOutFlag) {', 1)
save('corr7gfx.c', s)

# ---------------------------------------------------------------- corr7tmr.c
s = load('corr7tmr.c')
s = s.replace('     totalclock++;\n     if (!playingGameFlag) {', '     if (!playingGameFlag) {')
s = s.replace('     keytimerstuff();\n}', '}')
save('corr7tmr.c', s)

# ---------------------------------------------------------------- corr7snd.c
s = load('corr7snd.c')
s = s.replace('void cdecl\n', 'void\n')
save('corr7snd.c', s)

# ---------------------------------------------------------------- readcfg.c / profile.c
for name in ('readcfg.c', 'profile.c'):
    s = load(name)
    s = re.sub(r'itoa\(\s*([^,]+?),\s*([^,]+?),\s*10\s*\)', r'sprintf(\2, "%d", \1)', s)
    s = re.sub(r'itoa\(\s*([^,]+?),\s*([^,]+?),\s*16\s*\)', r'sprintf(\2, "%x", \1)', s)
    save(name, s)

# ---------------------------------------------------------------- mister_port.c (JonoF's Witchaven one): this game
s = load('mister_port.c')
s = s.replace('(set name jfSW_WHAVEN)', '(set name jfSW_CORR8)')
s = s.replace('static const char *const GameFiles[] = { "TILES000.ART", "PALETTE.DAT", "LOOKUP.DAT", "LEVEL1.MAP", NULL };',
              'static const char *const GameFiles[] = { "TILES000.ART", "PALETTE.DAT", "LOOKUP.DAT", "ABLEV1.MAP", "NAMES.H", NULL };')
s = re.sub(r'#define NO_GAME "[^"]*"', '#define NO_GAME "Corridor 8 was not found. Copy the game\'s Assets folder (TILES*.ART, PALETTE.DAT, LOOKUP.DAT, TABLES.DAT, the ABLEV*.MAP files, LOGO.SMK, CORR7.INI, the WAVS) to %s/."', s)
s = s.replace('games[0].id = "WHAVEN";', 'games[0].id = "CORR8";')
s = s.replace('games[0].name = "Witchaven";', 'games[0].name = "Corridor 8: Galactic Wars";')
save('mister_port.c', s)

print('ported')
