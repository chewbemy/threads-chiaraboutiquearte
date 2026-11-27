"""Renders a seamless looping MP4 (plum and gold, code only, no AI image credits).

render(subject, seed, out_path) -> out_path
Every random choice comes from `seed`, so each post looks different even when the
subject repeats. All motion is periodic over the clip, so the last frame flows
into the first and the video loops without a jump.
"""
import math
import os
import random
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import catalog

W, H = 1080, 1350          # 4:5, the tallest ratio Threads shows uncropped in feed
FPS = 30
SECONDS = 8
N = FPS * SECONDS
PHI = (1 + 5 ** 0.5) / 2

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
SANS = os.path.join(_FONT_DIR, "DejaVuSans.ttf")
SERIF = os.path.join(_FONT_DIR, "DejaVuSerif.ttf")
MONO = os.path.join(_FONT_DIR, "DejaVuSansMono.ttf")

GOLD = (222, 184, 92)
GOLD_HI = (250, 226, 156)
LAVENDER = (214, 196, 240)


def _font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- helpers
def _spaced(draw, center_x, y, text, font, fill, spacing):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = center_x - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


def _mask_points(mask, spacing, ox, oy):
    """Hex-grid sample of a mask's white area -> list of (x, y) in canvas space."""
    pts = []
    mw, mh = mask.size
    px = mask.load()
    row = 0
    y = spacing / 2
    while y < mh:
        x = spacing / 2 + (spacing / 2 if row % 2 else 0)
        while x < mw:
            if px[int(x), int(y)] > 127:
                pts.append((ox + x, oy + y))
            x += spacing
        y += spacing * 0.866
        row += 1
    return pts


def _glyph_mask(glyph, size, font_path=SANS):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    f = _font(font_path, int(size * 0.78))
    bbox = d.textbbox((0, 0), glyph, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), glyph, font=f, fill=255)
    return m


def _icon_mask(icon, size):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    c = size / 2
    r = size * 0.42
    lw = max(6, int(size * 0.07))

    def poly(n, rad, rot=0.0):
        return [(c + rad * math.cos(rot + 2 * math.pi * k / n), c + rad * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]

    if icon == "star8":
        pts = []
        for k in range(16):
            rad = r if k % 2 == 0 else r * 0.42
            a = -math.pi / 2 + math.pi * k / 8
            pts.append((c + rad * math.cos(a), c + rad * math.sin(a)))
        d.polygon(pts, fill=255)
    elif icon == "pentagram":
        p = poly(5, r, -math.pi / 2)
        d.line([p[0], p[2], p[4], p[1], p[3], p[0]], fill=255, width=lw, joint="curve")
        d.ellipse([c - r * 1.08, c - r * 1.08, c + r * 1.08, c + r * 1.08], outline=255, width=lw // 2)
    elif icon == "crescent":
        d.ellipse([c - r, c - r, c + r, c + r], fill=255)
        d.ellipse([c - r * 0.55, c - r * 1.05, c + r * 1.25, c + r * 0.95], fill=0)
    elif icon == "sun":
        d.ellipse([c - r * 0.45, c - r * 0.45, c + r * 0.45, c + r * 0.45], fill=255)
        for k in range(12):
            a = 2 * math.pi * k / 12
            d.line([(c + r * 0.6 * math.cos(a), c + r * 0.6 * math.sin(a)), (c + r * math.cos(a), c + r * math.sin(a))], fill=255, width=lw)
    elif icon == "lemniscate":
        pts = [(c + r * math.cos(t) / (1 + math.sin(t) ** 2), c + r * math.sin(t) * math.cos(t) / (1 + math.sin(t) ** 2))
               for t in [2 * math.pi * k / 200 for k in range(201)]]
        d.line(pts, fill=255, width=lw)
    elif icon == "wheel":
        d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=lw)
        d.ellipse([c - r * 0.25, c - r * 0.25, c + r * 0.25, c + r * 0.25], fill=255)
        for k in range(8):
            a = 2 * math.pi * k / 8
            d.line([(c, c), (c + r * math.cos(a), c + r * math.sin(a))], fill=255, width=lw // 2)
    elif icon == "scales":
        d.line([(c, c - r), (c, c + r)], fill=255, width=lw)
        d.line([(c - r, c - r * 0.55), (c + r, c - r * 0.55)], fill=255, width=lw)
        for sx in (-1, 1):
            x = c + sx * r * 0.8
            d.pieslice([x - r * 0.35, c - r * 0.2, x + r * 0.35, c + r * 0.4], 0, 180, fill=255)
            d.line([(x, c - r * 0.55), (x - r * 0.3, c + r * 0.1)], fill=255, width=lw // 3)
            d.line([(x, c - r * 0.55), (x + r * 0.3, c + r * 0.1)], fill=255, width=lw // 3)
        d.line([(c - r * 0.5, c + r), (c + r * 0.5, c + r)], fill=255, width=lw)
    elif icon == "bolt":
        d.polygon([(c + r * 0.15, c - r), (c - r * 0.45, c + r * 0.1), (c - r * 0.02, c + r * 0.1),
                   (c - r * 0.2, c + r), (c + r * 0.45, c - r * 0.15), (c + r * 0.02, c - r * 0.15)], fill=255)
    elif icon in ("triangle_up", "triangle_down", "triangle_up_bar", "triangle_down_bar"):
        up = icon.startswith("triangle_up")
        p = poly(3, r, -math.pi / 2 if up else math.pi / 2)
        d.line(p + [p[0]], fill=255, width=lw, joint="curve")
        if icon.endswith("_bar"):
            y = c + (r * 0.12 if up else -r * 0.12)
            d.line([(c - r * 0.75, y), (c + r * 0.75, y)], fill=255, width=lw)
    elif icon == "heart":
        pts = [(c + r * 0.06 * 16 * math.sin(t) ** 3,
                c - r * 0.06 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
               for t in [2 * math.pi * k / 200 for k in range(200)]]
        d.polygon(pts, fill=255)
    elif icon == "venus":
        return _glyph_mask("♀", size)
    elif icon == "square":
        d.rectangle([c - r * 0.8, c - r * 0.8, c + r * 0.8, c + r * 0.8], outline=255, width=lw)
        d.line([(c - r * 0.8, c - r * 0.8), (c + r * 0.8, c + r * 0.8)], fill=255, width=lw // 2)
        d.line([(c + r * 0.8, c - r * 0.8), (c - r * 0.8, c + r * 0.8)], fill=255, width=lw // 2)
    elif icon == "key":
        d.ellipse([c - r * 0.4, c - r, c + r * 0.4, c - r * 0.2], outline=255, width=lw)
        d.line([(c, c - r * 0.2), (c, c + r)], fill=255, width=lw)
        d.line([(c, c + r * 0.55), (c + r * 0.35, c + r * 0.55)], fill=255, width=lw)
        d.line([(c, c + r * 0.85), (c + r * 0.3, c + r * 0.85)], fill=255, width=lw)
    elif icon == "lantern":
        d.line([(c, c - r), (c, c - r * 0.7)], fill=255, width=lw // 2)
        d.polygon([(c - r * 0.35, c - r * 0.7), (c + r * 0.35, c - r * 0.7), (c + r * 0.5, c + r * 0.6), (c - r * 0.5, c + r * 0.6)], outline=255, width=lw)
        d.ellipse([c - r * 0.15, c - r * 0.1, c + r * 0.15, c + r * 0.3], fill=255)
        d.line([(c - r * 0.6, c + r * 0.7), (c + r * 0.6, c + r * 0.7)], fill=255, width=lw)
    elif icon == "rose":
        for k in range(5):
            a = 2 * math.pi * k / 5 - math.pi / 2
            x, y = c + r * 0.45 * math.cos(a), c + r * 0.45 * math.sin(a)
            d.ellipse([x - r * 0.42, y - r * 0.42, x + r * 0.42, y + r * 0.42], outline=255, width=lw // 2)
        d.ellipse([c - r * 0.2, c - r * 0.2, c + r * 0.2, c + r * 0.2], fill=255)
    else:
        d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=lw)
    return m


def _moon_mask(phase, size):
    """phase 0 = new, 0.5 = full; lit part on the right while waxing."""
    m = Image.new("L", (size, size), 0)
    px = m.load()
    c = size / 2
    r = size * 0.42
    k = math.cos(2 * math.pi * phase)           # 1 new, -1 full
    for y in range(size):
        dy = (y - c) / r
        if abs(dy) > 1:
            continue
        half = math.sqrt(1 - dy * dy)
        for x in range(size):
            dx = (x - c) / r
            if abs(dx) > half:
                continue
            term = k * half
            lit = dx > term if phase <= 0.5 else dx < -term
            if lit:
                px[x, y] = 255
    return m


def _golden_grid(draw, cx, cy, width, orient, color):
    """Golden-rectangle subdivision with its spiral, centred on (cx, cy)."""
    w, h = width, width / PHI
    x0, y0 = -w / 2, -h / 2
    segs, arcs = [], []
    x, y, rw, rh = x0, y0, w, h
    for i in range(9):
        d = i % 4
        if d == 0:
            s = rh; segs.append(((x + s, y), (x + s, y + rh))); arcs.append((x, y, s, 2)); x += s; rw -= s
        elif d == 1:
            s = rw; segs.append(((x, y + s), (x + rw, y + s))); arcs.append((x + rw - s, y, s, 3)); y += s; rh -= s
        elif d == 2:
            s = rh; segs.append(((x + rw - s, y), (x + rw - s, y + rh))); arcs.append((x + rw - s, y, s, 0)); rw -= s
        else:
            s = rw; segs.append(((x, y + rh - s), (x + rw, y + rh - s))); arcs.append((x, y + rh - s, s, 1)); rh -= s

    def tf(p):
        px_, py_ = p
        if orient & 1:
            px_ = -px_
        if orient & 2:
            py_ = -py_
        return cx + px_, cy + py_

    draw.rectangle([cx + x0, cy + y0, cx - x0, cy - y0], outline=color, width=1)
    for a, b in segs:
        draw.line([tf(a), tf(b)], fill=color, width=1)
    # quarter arcs: (square x, y, side, corner of the centre 0=tl 1=tr 2=br 3=bl)
    for sx, sy, s, corner in arcs:
        ccx = sx + (s if corner in (1, 2) else 0)
        ccy = sy + (s if corner in (2, 3) else 0)
        start = {0: 0, 1: 90, 2: 180, 3: 270}[corner]
        pts = []
        for t in range(0, 91, 5):
            a = math.radians(start + t)
            pts.append(tf((ccx + s * math.cos(a), ccy + s * math.sin(a))))
        draw.line(pts, fill=color, width=2)


# ---------------------------------------------------------------- scene
class Scene:
    def __init__(self, subject, seed):
        self.s = subject
        self.rng = random.Random(seed)
        r = self.rng
        self.hue_shift = r.uniform(-10, 10)
        self.gold = tuple(min(255, int(v + r.uniform(-12, 12))) for v in GOLD)
        self.cx, self.cy = W / 2, 500
        self.med_r = r.choice([250, 265, 280])
        self.ring_specs = []
        for i in range(r.randint(3, 5)):
            rad = self.med_r + 30 + i * r.choice([26, 32, 38])
            n = r.choice([36, 48, 60, 72, 90])
            m = r.choice([-2, -1, 1, 1, 2])
            dash = r.uniform(0.35, 0.65)
            self.ring_specs.append((rad, n, m, dash, r.choice([1, 2, 2])))
        self.stars = [(r.uniform(0, W), r.uniform(0, H), r.choice([1, 1, 1, 2, 2, 3]), r.randint(1, 3), r.random())
                      for _ in range(r.randint(170, 260))]
        self.shoot = (r.uniform(0.15, 0.6), r.uniform(-0.2, 0.2), r.uniform(0.0, 0.5))
        self.layout = r.choice(["classic", "tilted"])
        self.markers = []
        for _ in range(r.randint(5, 8)):
            a = r.uniform(0, 2 * math.pi)
            rad = r.uniform(self.med_r * 0.95, self.med_r * 1.7)
            x = min(W - 150, max(80, self.cx + rad * math.cos(a)))
            y = min(H - 380, max(150, self.cy + rad * math.sin(a)))
            self.markers.append((x, y, r.choice([1, 2]), r.random(), f"x: {int(x * 0.4)}  y: {int(y * 0.4)}"))
        self.static = self._static_layer()
        self.dots = self._main_dots()
        self.const = self._constellation()
        self.text_layer = self._text_layer()

    # --- static background: gradient, golden grid, fine geometry
    def _static_layer(self):
        r = self.rng
        bg = Image.new("RGB", (W, H))
        px = bg.load()
        inner = (int(58 + self.hue_shift), 22, int(74 - self.hue_shift / 2))
        outer = (13, 4, 21)
        gx, gy = self.cx + r.uniform(-120, 120), self.cy + r.uniform(-80, 80)
        maxd = math.hypot(W, H) * 0.62
        for y in range(H):
            for x in range(0, W, 2):
                t = min(1.0, math.hypot(x - gx, y - gy) / maxd) ** 1.3
                col = tuple(int(inner[i] * (1 - t) + outer[i] * t) for i in range(3))
                px[x, y] = col
                if x + 1 < W:
                    px[x + 1, y] = col
        over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(over)
        faint = self.gold + (46,)
        _golden_grid(d, self.cx, self.cy, r.choice([860, 900, 940]), r.randrange(4), faint)
        d.line([(self.cx, 60), (self.cx, H - 330)], fill=self.gold + (34,), width=1)
        d.line([(60, self.cy), (W - 60, self.cy)], fill=self.gold + (34,), width=1)
        for rad in (self.med_r, self.med_r * PHI * 0.62):
            d.ellipse([self.cx - rad, self.cy - rad, self.cx + rad, self.cy + rad], outline=self.gold + (70,), width=1)
        # tick marks on the medallion
        for k in range(120):
            a = 2 * math.pi * k / 120
            l = 14 if k % 10 == 0 else 6
            r0 = self.med_r
            d.line([(self.cx + r0 * math.cos(a), self.cy + r0 * math.sin(a)),
                    (self.cx + (r0 - l) * math.cos(a), self.cy + (r0 - l) * math.sin(a))], fill=self.gold + (90,), width=1)
        # corner frame
        m = 34
        d.rectangle([m, m, W - m, H - m], outline=self.gold + (80,), width=1)
        d.rectangle([m + 8, m + 8, W - m - 8, H - m - 8], outline=self.gold + (40,), width=1)
        bg = bg.convert("RGBA")
        bg.alpha_composite(over)
        return bg

    # --- the main symbol as golden dots
    def _main_dots(self):
        s = self.s
        size = int(self.med_r * 1.55)
        if s["kind"] in ("sign", "planet"):
            mask = _glyph_mask(s["glyph"], size)
        elif s["kind"] == "tarot":
            mask = _icon_mask(s["icon"], size)
        elif s["kind"] == "moon":
            mask = _moon_mask(s["phase"], size)
            if s["phase"] == 0.0:  # new moon: draw the outline only
                mask = Image.new("L", (size, size), 0)
                ImageDraw.Draw(mask).ellipse([size * 0.08, size * 0.08, size * 0.92, size * 0.92], outline=255, width=10)
        elif s["kind"] == "element":
            mask = _icon_mask(s["icon"], size)
        else:
            return []
        spacing = self.rng.choice([9, 10, 11])
        pts = _mask_points(mask, spacing, self.cx - size / 2, self.cy - size / 2)
        return [(x, y, self.rng.randint(1, 3), self.rng.random()) for x, y in pts]

    # --- constellation (signs: in the band under the medallion; constellations: inside it)
    def _constellation(self):
        key = self.s.get("constellation")
        if not key:
            return None
        name, ra, dec, stars, edges = catalog.CONSTELLATIONS[key]
        if self.s["kind"] == "constellation":
            bw = bh = self.med_r * 1.5
            bx, by = self.cx - bw / 2, self.cy - bh / 2
        else:
            bw, bh = 620, 210
            bx, by = self.cx - bw / 2, 805
        flip = self.layout == "tilted" and self.s["kind"] == "constellation"
        rot = math.radians(self.rng.uniform(-8, 8))
        pts = []
        for x, y, sz in stars:
            ux, uy = (1 - x if flip else x) - 0.5, y - 0.5
            ux, uy = ux * math.cos(rot) - uy * math.sin(rot), ux * math.sin(rot) + uy * math.cos(rot)
            pts.append((bx + (ux + 0.5) * bw, by + (uy + 0.5) * bh, sz))
        order = list(edges)
        return {"pts": pts, "edges": order, "ra": ra, "dec": dec}

    def _text_layer(self):
        s = self.s
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        title = s["name"].upper()
        size = 92 if len(title) <= 9 else (76 if len(title) <= 13 else 62)
        TY = 1050
        _spaced(d, W / 2, TY, title, _font(SERIF, size), self.gold + (255,), spacing=size * 0.18)
        _spaced(d, W / 2, TY + size + 26, s["subtitle"], _font(SANS, 30), LAVENDER + (235,), spacing=7)
        d.line([(W / 2 - 150, TY + size + 12), (W / 2 + 150, TY + size + 12)], fill=self.gold + (150,), width=1)
        for sx in (-1, 1):
            x = W / 2 + sx * 170
            y = TY + size + 12
            d.polygon([(x, y - 5), (x + 5, y), (x, y + 5), (x - 5, y)], fill=self.gold + (200,))
        _spaced(d, W / 2, H - 82, "CHIARA BOUTIQUE ARTE", _font(SANS, 20), self.gold + (150,), spacing=6)
        mono = _font(MONO, 19)
        if s["kind"] == "tarot":
            _spaced(d, W / 2, 150, s["numeral"], _font(SERIF, 64), self.gold + (235,), spacing=10)
        if self.const:
            d.text((70, 70), f"RA  {self.const['ra']}", font=mono, fill=LAVENDER + (170,))
            d.text((70, 96), f"DEC {self.const['dec']}", font=mono, fill=LAVENDER + (170,))
        elif s["kind"] == "sign":
            pass
        info = {"sign": f"{s.get('element', '').upper()}  ·  {s.get('ruler', '').upper()}"}.get(s["kind"])
        if info:
            d.text((W - 70 - d.textlength(info, font=mono), 70), info, font=mono, fill=LAVENDER + (170,))
        return lay

    # --- per-frame drawing
    def frame(self, i):
        p = i / N
        img = self.static.copy()
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sharp)

        for x, y, sz, k, ph in self.stars:
            b = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * (k * p + ph)))
            a = int(255 * b * (0.5 if sz == 1 else 0.85))
            col = LAVENDER if sz < 3 else GOLD_HI
            sd.ellipse([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2], fill=col + (a,))
            if sz == 3:
                gd.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD_HI + (int(a * 0.6),))

        for rad, n, m, dash, lw in self.ring_specs:
            off = 2 * math.pi / n * m * p * 4   # integer number of dash periods per loop
            for k in range(n):
                a0 = off + 2 * math.pi * k / n
                a1 = a0 + 2 * math.pi / n * dash
                sd.arc([self.cx - rad, self.cy - rad, self.cx + rad, self.cy + rad],
                       math.degrees(a0), math.degrees(a1), fill=self.gold + (120,), width=lw)

        mono = _font(MONO, 15)
        for x, y, k, ph, label in self.markers:
            b = 0.5 + 0.5 * math.sin(2 * math.pi * (k * p + ph))
            rr = 4 + 3 * b
            sd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD + (int(120 + 135 * b),))
            gd.ellipse([x - rr * 2.5, y - rr * 2.5, x + rr * 2.5, y + rr * 2.5], fill=GOLD + (int(80 * b),))
            sd.text((x + 12, y - 8), label, font=mono, fill=LAVENDER + (int(90 + 110 * b),))

        breathe = 0.5 + 0.5 * math.sin(2 * math.pi * p)
        for x, y, sz, ph in self.dots:
            b = 0.55 + 0.45 * math.sin(2 * math.pi * (2 * p + ph))
            rr = 1.6 + sz * 0.7
            sd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD_HI + (int(170 + 85 * b),))
            if b > 0.75:
                gd.ellipse([x - rr * 2.2, y - rr * 2.2, x + rr * 2.2, y + rr * 2.2], fill=self.gold + (int(110 * b),))
        if self.dots:
            gr = self.med_r * (0.55 + 0.05 * breathe)
            gd.ellipse([self.cx - gr, self.cy - gr, self.cx + gr, self.cy + gr], fill=(120, 60, 150, int(26 + 20 * breathe)))

        if self.const:
            pts, edges = self.const["pts"], self.const["edges"]
            start, end = 0.06, 0.58
            fade = 1.0 if p < 0.86 else max(0.0, 1 - (p - 0.86) / 0.14)
            for j, (a, b_) in enumerate(edges):
                t0 = start + (end - start) * j / len(edges)
                t1 = start + (end - start) * (j + 1) / len(edges)
                if p < t0:
                    continue
                f = min(1.0, (p - t0) / (t1 - t0))
                xa, ya, _ = pts[a]
                xb, yb, _ = pts[b_]
                xe, ye = xa + (xb - xa) * f, ya + (yb - ya) * f
                sd.line([(xa, ya), (xe, ye)], fill=GOLD_HI + (int(200 * fade),), width=2)
                gd.line([(xa, ya), (xe, ye)], fill=self.gold + (int(120 * fade),), width=6)
            greek = "αβγδεζηθικ"
            small = _font(SANS, 16)
            for j, (x, y, sz) in enumerate(pts):
                tw = 0.6 + 0.4 * math.sin(2 * math.pi * (p * 2 + j * 0.13))
                rr = 3 + sz * 1.6
                sd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD_HI + (int(230 * tw + 25),))
                gd.ellipse([x - rr * 3, y - rr * 3, x + rr * 3, y + rr * 3], fill=self.gold + (int(90 * tw),))
                sd.text((x + rr + 5, y - rr - 14), greek[j % len(greek)], font=small, fill=LAVENDER + (150,))

        # one shooting star per loop, entering and leaving off-canvas
        sy0, slope, t0 = self.shoot
        t = (p - t0) % 1.0
        if t < 0.18:
            q = t / 0.18
            x = -150 + q * (W + 300)
            y = H * sy0 + slope * x
            for k in range(14):
                xx = x - k * 9
                yy = y - slope * k * 9
                sd.ellipse([xx - 1.5, yy - 1.5, xx + 1.5, yy + 1.5], fill=GOLD_HI + (int(220 * (1 - k / 14)),))

        glow = glow.filter(ImageFilter.GaussianBlur(7))
        img.alpha_composite(glow)
        img.alpha_composite(sharp)
        img.alpha_composite(self.text_layer)
        return img.convert("RGB")


def _ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg  # pip wheel with a static ffmpeg, no apt-get needed
    return imageio_ffmpeg.get_ffmpeg_exe()


def render(subject, seed, out_path, gif_path=None):
    scene = Scene(subject, seed)
    ff = _ffmpeg()
    cmd = [ff, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        proc.stdin.write(scene.frame(i).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    if gif_path:
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", out_path, "-vf",
                        "fps=15,scale=540:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse",
                        "-loop", "0", gif_path], check=True)
    return out_path
