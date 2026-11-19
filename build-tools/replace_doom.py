"""Corridor 8: the DOOM placeholder sprites replaced by the game's own art, in
the ART files and corr7.ini (no code change). usage: replace_doom.py <set folder>
- enemies HUMAN1 (3832-3882) and ENEMY1 (3883-3931): the frames of the game's
  own ENEMY2 probe drone (1786-1815), role by role (walk, fire, pain, die, gore)
- weapons: corr7.ini Pistol / Chain Gun -> the GGG laser gun (1295-1304),
  Missile Launcher / BFG9000 -> the G laser gun (1305-1307); the DOOM chaingun
  and rocket launcher tiles (3942-3950) are blanked
- STATUSBARPIC 3830: a plain dark-metal bar with the same labels
- BACKGROUNDPIC 3831: the starfield of the new title (menu background)
The original tiles015.art stays as tiles015.art.doom.bak (not shipped)."""
import os, sys, struct, random
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arttiles import Art
c = sys.argv[1]
a = Art(c, orig15=True)   # start from the DOOM original of tiles015 (title gets redone below)
picanm = {}
# read picanm of file 15 and 6/7 (we keep ENEMY2's for copied frames)
def read_picanm(n):
    p = os.path.join(c, 'tiles%03d.art' % n)
    if n == 15 and os.path.exists(p + '.doom.bak'): p += '.doom.bak'
    with open(p, 'rb') as fh:
        ver, num, start, end = struct.unpack('<iiii', fh.read(16)); cnt = end - start + 1
        fh.read(4 * cnt); d = fh.read(4 * cnt)
        return start, [d[4 * t:4 * t + 4] for t in range(cnt)]
for f in set(a.files.values()):
    st, pa = read_picanm(f)
    for i, v in enumerate(pa): picanm[st + i] = v
changed = {}
def put(dst, src):
    changed[dst] = (a.tiles[src], picanm[src])
def put_img(dst, img_p):   # a paletted PIL image, index 255 = transparent
    w, h = img_p.size; d = img_p.tobytes(); col = bytearray(w * h)
    for y in range(h):
        for x in range(w): col[x * h + y] = d[y * w + x]
    changed[dst] = ((w, h, bytes(col)), b'\0\0\0\0')
def blank(dst): changed[dst] = ((0, 0, b''), b'\0\0\0\0')
# --- enemies: ENEMY2 roles
E2_WALK = list(range(1786, 1806)); E2_FIRE = [1806, 1807, 1808]; E2_PAIN = 1809; E2_DIE = list(range(1810, 1816))
def enemy(walk0, fire0, pain0, die0, gore0, end):
    for i, t in enumerate(range(walk0, fire0)): put(t, E2_WALK[i % len(E2_WALK)])
    for i, t in enumerate(range(fire0, pain0)): put(t, E2_FIRE[i % len(E2_FIRE)])
    for t in range(pain0, die0): put(t, E2_PAIN)
    for i, t in enumerate(range(die0, gore0)): put(t, E2_DIE[min(i, len(E2_DIE) - 1)])
    for i, t in enumerate(range(gore0, end + 1)): put(t, E2_DIE[-3 + (i % 3)])
enemy(3832, 3852, 3862, 3867, 3874, 3882)   # HUMAN1
enemy(3883, 3903, 3913, 3918, 3923, 3931)   # ENEMY1
for t in range(3942, 3951): blank(t)        # DOOM chaingun + rocket launcher
# --- status bar 320x32 and menu background 320x200 in the game palette
pal = Image.new('P', (1, 1)); pal.putpalette(a.flat[:765] + [0, 0, 0])
def quant(img):
    q = img.quantize(palette=pal, dither=Image.Dither.NONE); d = bytearray(q.tobytes())
    for i, v in enumerate(d):
        if v == 255: d[i] = 254
    q = Image.frombytes('P', q.size, bytes(d)); return q
bar = Image.new('RGB', (320, 32), (0, 0, 0)); px = bar.load()
for y in range(32):
    for x in range(320):
        g = 52 + int(26 * (1 - abs(y - 14) / 16)); px[x, y] = (g, g + 2, g + 6)
dr = ImageDraw.Draw(bar)
from PIL import ImageFont
try: f9 = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 9); f7 = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 7)
except Exception: f9 = f7 = ImageFont.load_default()
# The game draws three numbers on the bar (corr7plr.c PLR_updateStatus*): 14x16 digits centred
# on y 180 (bar line 12, so lines 4..20), the string centred on x 23 (ammo), 73 (health) and 123
# (aliens left). Cells of 50 pixels around those centres, the label under each number; the
# right part of the bar is a plain panel. (2026-11-17: the first bar's labels did not line up.)
for x in (48, 98, 148): dr.line((x, 2, x, 29), fill=(28, 30, 36)); dr.line((x + 1, 2, x + 1, 29), fill=(96, 100, 110))
dr.rectangle((0, 0, 319, 31), outline=(110, 114, 124))
for txt, cx in (('AMMO', 23), ('HEALTH', 73), ('ALIENS', 123)):
    w = dr.textlength(txt, font=f9); dr.text((cx - w / 2, 21), txt, font=f9, fill=(220, 220, 230))
for cx in (23, 73, 123): dr.rectangle((cx - 22, 3, cx + 22, 20), fill=(10, 10, 14))
w = dr.textlength('CORRIDOR 8', font=f9); dr.text((234 - w / 2, 7), 'CORRIDOR 8', font=f9, fill=(150, 154, 166))
w = dr.textlength('GALACTIC WARS', font=f7); dr.text((234 - w / 2, 19), 'GALACTIC WARS', font=f7, fill=(120, 124, 136))
put_img(3830, quant(bar))
bg = Image.new('RGB', (320, 200), (0, 0, 0)); px = bg.load(); random.seed(8)
for y in range(200):
    for x in range(320): px[x, y] = (0, int(4 + 10 * y / 200), int(18 + 30 * y / 200))
for _ in range(220):
    x, y = random.randrange(320), random.randrange(200); b = random.choice((90, 140, 200, 255)); px[x, y] = (b, b, min(255, b + 20))
put_img(3831, quant(bg))
# the title made earlier (tiles015.art as it stands now holds it): keep it
cur = Art(c, orig15=False); changed[3829] = (cur.tiles[3829], b'\0\0\0\0')
# --- write every ART file that changed
byfile = {}
for t in changed: byfile.setdefault(a.files[t], []).append(t)
for f, ts in byfile.items():
    p = os.path.join(c, 'tiles%03d.art' % f)
    src = p + '.doom.bak' if (f == 15 and os.path.exists(p + '.doom.bak')) else p
    with open(src, 'rb') as fh:
        ver, num, start, end = struct.unpack('<iiii', fh.read(16)); cnt = end - start + 1
        xs = list(struct.unpack('<%dh' % cnt, fh.read(2 * cnt))); ys = list(struct.unpack('<%dh' % cnt, fh.read(2 * cnt))); pa = bytearray(fh.read(4 * cnt))
        data = [fh.read(xs[t] * ys[t]) for t in range(cnt)]
    for t in ts:
        (w, h, d), an = changed[t]; i = t - start; xs[i], ys[i], data[i] = w, h, d; pa[4 * i:4 * i + 4] = an
    with open(p, 'wb') as fh:
        fh.write(struct.pack('<iiii', ver, num, start, end)); fh.write(struct.pack('<%dh' % cnt, *xs)); fh.write(struct.pack('<%dh' % cnt, *ys)); fh.write(bytes(pa))
        for d in data: fh.write(d)
    print('tiles%03d.art: %d tiles replaced' % (f, len(ts)))
# --- corr7.ini: the weapons
p = os.path.join(c, 'corr7.ini'); s = open(p, encoding='latin1', newline='').read()
import re
def section(name, repl):
    global s
    m = re.search(r'(?s)(\[' + name + r'\].*?)(?=\n\[|\Z)', s); body = m.group(1); new = body
    for k, v in repl.items(): new = re.sub(r'(?m)^(' + k + r'\s*=\s*)\S*', lambda mm: mm.group(1) + v, new)
    s = s.replace(body, new); print(name, repl)
for w in ('WEAPON1', 'WEAPON4'): section(w, {'HOLDPIC1': 'GGGHOLDPIC', 'FIREPIC1': 'GGGFIREAPIC', 'FIREPIC2': 'GGGFIREBPIC'})
for w in ('WEAPON5', 'WEAPON7'): section(w, {'HOLDPIC1': 'GHOLDPIC', 'FIREPIC1': 'GFIREAPIC', 'FIREPIC2': 'GFIREBPIC'})
if not os.path.exists(p + '.doom.bak'): open(p + '.doom.bak', 'w', encoding='latin1', newline='').write(open(p, encoding='latin1', newline='').read())
open(p, 'w', encoding='latin1', newline='').write(s); print('corr7.ini written')
