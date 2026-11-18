"""Corridor 8 ART helpers: read every tiles###.art of a folder (tiles015 from
its .doom.bak if present) into one index; sheets of tile ranges as PNG."""
import os, struct
from PIL import Image, ImageDraw
class Art:
    def __init__(self, folder, orig15=True):
        self.folder = folder; self.tiles = {}; self.files = {}
        pal = open(os.path.join(folder, 'palette.dat'), 'rb').read()[:768]
        self.flat = [min(255, (pal[i] << 2) | (pal[i] >> 4)) for i in range(768)]
        for n in range(32):
            p = os.path.join(folder, 'tiles%03d.art' % n)
            if not os.path.exists(p): continue
            if n == 15 and orig15 and os.path.exists(p + '.doom.bak'): p = p + '.doom.bak'
            with open(p, 'rb') as fh:
                ver, num, start, end = struct.unpack('<iiii', fh.read(16)); cnt = end - start + 1
                xs = struct.unpack('<%dh' % cnt, fh.read(2 * cnt)); ys = struct.unpack('<%dh' % cnt, fh.read(2 * cnt)); fh.read(4 * cnt)
                for t in range(cnt):
                    self.tiles[start + t] = (xs[t], ys[t], fh.read(xs[t] * ys[t]))
                    self.files[start + t] = n
    def image(self, n):
        w, h, d = self.tiles[n]
        if w * h == 0: return None
        im = Image.frombytes('P', (h, w), d).transpose(Image.Transpose.TRANSPOSE); im.putpalette(self.flat); return im
    def sheet(self, path, lo, hi, cols=10):
        ns = list(range(lo, hi + 1)); cw = max(self.tiles[n][0] for n in ns) + 4; ch = max(self.tiles[n][1] for n in ns) + 14
        rows = (len(ns) + cols - 1) // cols; im = Image.new('RGB', (cols * cw, rows * ch), (60, 0, 60)); dr = ImageDraw.Draw(im)
        for i, n in enumerate(ns):
            t = self.image(n)
            if t is not None: im.paste(t.convert('RGB'), ((i % cols) * cw, (i // cols) * ch + 12))
            dr.text(((i % cols) * cw, (i // cols) * ch), '%d %dx%d' % (n, self.tiles[n][0], self.tiles[n][1]), fill=(255, 255, 0))
        im.save(path); return im.size
