# Corridor 8: Galactic Wars on JonoF's jfbuild (MiSTer branch): fresh copies of
# the DOS sources, the port's modules, the transformations, a build, and a
# classification of what is left. Idempotent: run it after every script change.
S=/mnt/c/Users/Jess/AppData/Local/Temp/claude/d3c88340bd34ded3/877f9e48-85c9-4030-aad6-fabad4d7e72d/scratchpad
export PATH=~/ionfury/bin:$PATH
T=~/ionfury/tier2/jfcorr8; C="/mnt/c/Users/Jess/Desktop/EDUKE32/Corridor8GalacticWars/CORR8 SRC"; JF=~/ionfury/tier2/jfwhaven/src
rm -rf $T && cp -r ~/ionfury/tier2/jfwhaven $T && rm -rf $T/build $T/src
mkdir -p $T/src
# the modules the makefile builds (the upper-case files are the newest)
for f in CORR7.C CORR7ACT.C CORR7CFG.C CORR7EFF.C CORR7ENG.C CORR7GAM.C CORR7GFX.C CORR7KBD.C CORR7MEN.C CORR7MUL.C CORR7PLR.C CORR7SMK.C CORR7SND.C CORR7TMR.C CORR7WEP.C PROFILE.C READCFG.C; do
  lc=$(echo $f | tr A-Z a-z); src=$(find "$C" -maxdepth 1 -iname "$f" | head -1); [ -n "$src" ] && tr -d '\r' < "$src" | expand -t 4 > $T/src/$lc || echo "missing $f"
done
for f in $(cd "$C" && ls | grep -i '\.h$\|\.def$'); do lc=$(echo $f | tr A-Z a-z); tr -d '\r' < "$C/$f" | expand -t 4 > $T/src/$lc; done
# JonoF's modules that carry over, and the port's own
for f in b5compat.c version.c version.h mister_port.c mister_port.h; do cp $JF/$f $T/src/$f; done
cp "$S/tier2/c8/sos.h" "$S/tier2/c8/sosemu.c" "$S/tier2/c8/c8port.c" "$S/tier2/c8/c8port.h" $T/src/
cp "$S/tier2/c8/sos.h" $T/src/sosm.h
# the DOS compiler's long is the engine's int
for f in $T/src/corr7*.c $T/src/corr7*.def $T/src/corr7.h $T/src/icorp.h $T/src/c7cntrl.h $T/src/readcfg.c $T/src/readcfg.def $T/src/profile.c $T/src/profile.h; do [ -f $f ] && sed -i -E 's/\blong\b/int/g' $f; done
# the DOS headers and the libraries the port does not have: their includes dropped
python3 - $T <<'PY'
import sys, glob, os, re
t = sys.argv[1]
B = chr(92)
have = set(os.path.basename(f).lower() for f in glob.glob(t + '/src/*.h') + glob.glob(t + '/src/*.def') + glob.glob(t + '/jfbuild/include/*.h') + glob.glob(t + '/jfaudiolib/include/*.h'))
for f in glob.glob(t + '/src/*.[ch]') + glob.glob(t + '/src/*.def'):
    if os.path.basename(f) in ('sosemu.c', 'c8port.c', 'c8port.h', 'sos.h', 'sosm.h', 'mister_port.c', 'b5compat.c', 'version.c'):
        continue
    s = open(f, encoding='latin1', newline='').read()
    s = s.replace('<sys' + B + 'types.h>', '<sys/types.h>').replace('<sys' + B + 'stat.h>', '<sys/stat.h>')
    s = re.sub(r'(?mi)^#include[ \t]*<(memcheck|dos|conio|graph|malloc|windows|io|process|i86|bios|direct|share|pmpro|netnow|smack|dpmi)' + B + '.h>[^\n]*\n', '', s)
    def keep(m):
        name = m.group(1).lower()
        return m.group(0) if name in have else '// ' + m.group(0) + '  /* not in the port */'
    s = re.sub(r'(?m)^#include[ \t]*"([^"]+)"', keep, s)
    open(f, 'w', encoding='latin1', newline='').write(s)
PY
python3 "$S/tier2/c8/port_c8.py" $T || exit 1
python3 "$S/tier2/patch_cheats.py" $T jfcorr8 || exit 1
python3 "$S/tier2/patch_c8menu.py" $T || exit 1
python3 "$S/tier2/patch_c8joy.py" $T || exit 1
python3 "$S/tier2/patch_c8crash.py" $T || exit 1
python3 "$S/tier2/patch_c8use.py" $T || exit 1
# CMake: the Witchaven list with the game's modules in place of Witchaven's
python3 - $T <<'PY'
import os, sys, re
t = sys.argv[1]
s = open(os.path.join(t, 'CMakeLists.txt')).read()
s = s.replace('project(jfwhaven C)', 'project(jfcorr8 C)').replace('add_executable(jfwhaven', 'add_executable(jfcorr8').replace('jfwhaven PRIVATE', 'jfcorr8 PRIVATE')
mods = ['src/' + f for f in sorted(os.listdir(os.path.join(t, 'src'))) if f.endswith('.c')]
s = re.sub(r'(?m)^\tsrc/[a-z0-9_]+\.c\n', '', s)
s = s.replace('\tlibsmacker/smacker.c\n', '\tlibsmacker/smacker.c\n\n\t' + '\n\t'.join(mods) + '\n')
open(os.path.join(t, 'CMakeLists.txt'), 'w').write(s)
print('modules:', len(mods))
PY
R=~/ionfury/EDuke32_MiSTer; PREFIX=$R/build/sdl/mister/prefix
BT=Release; CF="-funwind-tables -fno-omit-frame-pointer"; [ -n "$C8DEBUG" ] && { BT=Debug; CF="-O0 -fno-omit-frame-pointer -funwind-tables -g"; }
cmake -S $T -B $T/build -DCMAKE_BUILD_TYPE=$BT "-DCMAKE_C_FLAGS=$CF" -DCMAKE_TOOLCHAIN_FILE=$R/hybrid/toolchain/mister.cmake -DCMAKE_FIND_ROOT_PATH=$PREFIX -DCMAKE_PREFIX_PATH=$PREFIX -DMISTER_HYBRID=ON "-DCMAKE_EXE_LINKER_FLAGS=-no-pie -static-libgcc" > $T/cmake.log 2>&1 || { tail -5 $T/cmake.log; exit 1; }
cmake --build $T/build -j"$(nproc)" -- -k > $T/build.log 2>&1
echo "== errors per file"; grep -o "src/[a-z0-9_]*\.[ch]:[0-9]*:[0-9]*: error" $T/build.log | cut -d: -f1 | sort | uniq -c | sort -rn
echo "== error kinds"; grep "error:" $T/build.log | sed -E "s/.*error: //" | sed -E "s/'[^']*'/X/g" | sort | uniq -c | sort -rn | head -24
echo "== undefined (link)"; grep "undefined reference" $T/build.log | sed -E "s/.*undefined reference to .([A-Za-z_0-9]+).*/\1/" | sort | uniq -c | sort -rn | head -40
ls -la $T/build/jfcorr8 2>/dev/null
