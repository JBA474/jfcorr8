"""Corridor 8 title picture (tile 3829, TITLEPIC): CORR8_title_source.png
(320x200, the "CORRIDOR 8 / GALACTIC WARS" lettering over a starfield) with
the subtitle line redrawn as "1996 PROTOTYPE" only (Jess, 2026-11-17: take
"MiSTer Port" off the splash). The band of the old subtitle is repainted
with the starfield's own background and a few stars, the new text is
centred in the same place, and the picture is quantized to the game palette
and written into tiles015.art of the set folder.
usage: make_title.py <set folder>   (writes build-tools/CORR8_title_source.png too)"""
import os, sys, struct, random
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arttiles import Art
c = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(here, 'CORR8_title_source.png')
# the picture as it was with the old subtitle, kept as the pristine input
orig = os.path.join(here, 'CORR8_title_source.misterport.png')
img = Image.open(orig if os.path.exists(orig) else src_path).convert('RGB'); px = img.load()
# the subtitle band: lines 149..163 (the old "1996 PROTOTYPE - MiSTer PORT", x 90..230), x 40..280
band = (40, 149, 280, 164)
# repainted with the starfield left of the old text, on the same lines (the
# background darkens towards the top, so a strip from elsewhere shows as a band)
strip = img.crop((band[0], band[1], 72, band[3]))
for x in range(band[0], band[2], strip.width):
    img.paste(strip.crop((0, 0, min(strip.width, band[2] - x), strip.height)), (x, band[1]))
dr = ImageDraw.Draw(img)
try: f = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 11)
except Exception: f = ImageFont.load_default()
txt = '1996 PROTOTYPE'; w = dr.textlength(txt, font=f)
dr.text((160 - w / 2, 150), txt, font=f, fill=(190, 192, 200))
img.save(src_path); print('source png updated')
# quantize to the game palette (index 255 is transparent in Build: keep it off)
a = Art(c, orig15=False)
pal = Image.new('P', (1, 1)); pal.putpalette(a.flat[:765] + [0, 0, 0])
q = img.quantize(palette=pal, dither=Image.Dither.NONE); d = bytearray(q.tobytes())
for i, v in enumerate(d):
    if v == 255: d[i] = 254
w, h = q.size
col = bytes(d[y * w + x] for x in range(w) for y in range(h))  # Build tiles are column-major
p = os.path.join(c, 'tiles015.art')
with open(p, 'rb') as fh:
    ver, num, start, end = struct.unpack('<iiii', fh.read(16)); cnt = end - start + 1
    xs = list(struct.unpack('<%dh' % cnt, fh.read(2 * cnt))); ys = list(struct.unpack('<%dh' % cnt, fh.read(2 * cnt))); pa = bytearray(fh.read(4 * cnt))
    data = [fh.read(xs[t] * ys[t]) for t in range(cnt)]
i = 3829 - start; assert (xs[i], ys[i]) == (w, h), (xs[i], ys[i]); data[i] = col
with open(p, 'wb') as fh:
    fh.write(struct.pack('<iiii', ver, num, start, end)); fh.write(struct.pack('<%dh' % cnt, *xs)); fh.write(struct.pack('<%dh' % cnt, *ys)); fh.write(bytes(pa))
    for dd in data: fh.write(dd)
print('tiles015.art: tile 3829 written')
