S=/mnt/c/Users/Jess/AppData/Local/Temp/claude/d3c88340bd34ded3/877f9e48-85c9-4030-aad6-fabad4d7e72d/scratchpad
export PATH=~/ionfury/bin:$PATH
for g in jftekwar jfwhaven; do
  T=~/ionfury/tier2/$g
  cp "$S/dl/jf/jfSW_MiSTer/jfsw/jfbuild/src/sdlayer2.c" $T/jfbuild/src/sdlayer2.c; python3 "$S/tier2/patch_padkeys.py" $T/jfbuild || exit 1; python3 "$S/tier2/patch_osdres.py" $T/jfbuild || exit 1; python3 "$S/tier2/patch_wide.py" $T || exit 1; python3 "$S/tier2/patch_whpad.py" $T || exit 1; [ "$g" = jftekwar ] && { python3 "$S/tier2/patch_tekpad.py" $T || exit 1; }
  python3 "$S/tier2/patch_rumble.py" $T || exit 1; [ "$g" = jftekwar ] && { python3 "$S/tier2/patch_tekrumble.py" $T || exit 1; }; [ "$g" = jfwhaven ] && { python3 "$S/tier2/patch_whrumble.py" $T || exit 1; }; python3 "$S/tier2/patch_cheats.py" $T $g || exit 1
  cmake --build $T/build -j"$(nproc)" > $T/build.log 2>&1 || { echo "$g build FAILED"; grep -n "error" $T/build.log | head -5; exit 1; }; echo "$g build exit 0"
done
cp ~/ionfury/tier2/jftekwar/build/jftekwar "$S/tier2/tekwar/jftekwar"; cp ~/ionfury/tier2/jfwhaven/build/jfwhaven "$S/tier2/whaven/jfwhaven"; ls -la "$S/tier2/tekwar/jftekwar" "$S/tier2/whaven/jfwhaven"
echo "BUILD OK"
