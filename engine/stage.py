#!/usr/bin/env python3
"""ENGINE LAYER — stage core: canvas, palette, fonts, background, easing.

Topic-blind. Everything here is mechanism: a 1280x720 slate stage with a
central spotlight pool, one locked palette, and the math helpers every
archetype and episode choreography builds on.

Palette discipline (worked example — the Turing episode): brass/gold and
warm beige are reserved for physical props (read/write head, balance
scale, blackboard stand), cyan/teal glow only for diagram lines, orange
only for emphasis numbers, purple only for the "NP" class. An episode
keeps the palette and re-skins the props; it does not invent new colors
mid-video.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1280, 720
FPS = 30

# ---------------------------------------------------------------- fonts
# Font roles are resolved from candidate paths so the same code runs on
# Linux (Noto/DejaVu), macOS, or a box with fonts elsewhere. Override any
# role with an environment variable, e.g. SEV_FONT_CJK=/path/to/font.ttc.
_DEJAVU = "/usr/share/fonts/truetype/dejavu"
_NOTO = "/usr/share/fonts/opentype/noto"


def _first(candidates):
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return candidates[-1]


CJK = _first([os.environ.get("SEV_FONT_CJK"),
              f"{_NOTO}/NotoSansCJK-Regular.ttc",
              "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
              "/System/Library/Fonts/PingFang.ttc",
              f"{_DEJAVU}/DejaVuSans.ttf"])
CJKB = _first([os.environ.get("SEV_FONT_CJKB"),
               f"{_NOTO}/NotoSansCJK-Bold.ttc",
               "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
               "/System/Library/Fonts/PingFang.ttc",
               f"{_DEJAVU}/DejaVuSans-Bold.ttf"])
SERIFCJK = _first([os.environ.get("SEV_FONT_SERIFCJK"),
                   f"{_NOTO}/NotoSerifCJK-Regular.ttc",
                   "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
                   CJK])
SERIFCJKB = _first([os.environ.get("SEV_FONT_SERIFCJKB"),
                    f"{_NOTO}/NotoSerifCJK-Bold.ttc",
                    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttc",
                    CJKB])
SERIF = _first([os.environ.get("SEV_FONT_SERIF"),
                f"{_DEJAVU}/DejaVuSerif.ttf",
                "/System/Library/Fonts/Supplemental/Georgia.ttf",
                CJK])
SERIFB = _first([os.environ.get("SEV_FONT_SERIFB"),
                 f"{_DEJAVU}/DejaVuSerif-Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                 CJKB])
SANS = _first([os.environ.get("SEV_FONT_SANS"),
               f"{_DEJAVU}/DejaVuSans.ttf",
               "/System/Library/Fonts/Helvetica.ttc",
               CJK])
SANSB = _first([os.environ.get("SEV_FONT_SANSB"),
                f"{_DEJAVU}/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                CJKB])

_fc = {}


def F(path, size):
    """Cached font loader. F(SERIFB, 38) -> a 38px bold serif font."""
    size = max(6, int(round(size)))
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


# ---------------------------------------------------------------- palette
BEIGE = (232, 220, 192)
PAPER = (238, 230, 205)
PAPER_D = (214, 202, 168)
INK = (43, 38, 28)
GOLD = (217, 164, 65)
GOLD_L = (240, 200, 110)
BRASS = (186, 148, 78)
BRASS_D = (128, 98, 48)
CYAN = (64, 205, 225)
TEAL = (66, 200, 185)
PBLUE = (96, 170, 215)
PURPLE = (138, 127, 214)
PURPLE_L = (176, 168, 235)
ORANGE = (255, 159, 46)
GREEN = (84, 224, 138)
GREEN_D = (40, 170, 100)
RED = (235, 84, 70)
WHITE = (255, 255, 255)
GREY = (150, 155, 165)
DIMTXT = (196, 202, 212)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def seg(t, t0, t1):
    """Progress of time t through the window [t0, t1], clamped to [0, 1].

    This is the one timing primitive every animation uses:
    seg(u, 2.0, 3.5) is 0 before 2.0s, 1 after 3.5s, smooth in between
    when composed with ease_out/ease_io.
    """
    return clamp((t - t0) / (t1 - t0))


def mix(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def text_c(d, cx, y, s, font, fill, **kw):
    """Draw text horizontally centered at cx. Returns the text width."""
    w = d.textlength(s, font=font)
    d.text((cx - w / 2, y), s, font=font, fill=fill, **kw)
    return w


# ---------------------------------------------------------------- backdrop
def make_bg():
    """The stage: deep slate-blue gradient, central spotlight pool,
    soft floor sheen. NOT pure black — the reference videos use a dark
    slate stage with a light pool the props stand in."""
    top = (10, 15, 24)
    mid = (30, 43, 62)
    bot = (6, 8, 13)
    bg = Image.new("RGB", (W, H))
    px = bg.load()
    cx, cy = 640, 350
    for y in range(H):
        if y < 400:
            base = mix(top, mid, y / 400)
        else:
            base = mix(mid, bot, (y - 400) / 320)
        for x in range(0, W, 4):
            dist = math.hypot((x - cx) / 1.35, (y - cy)) / 560.0
            glow = max(0.0, 1.0 - dist) ** 2 * 26
            c = tuple(min(255, int(base[i] + glow)) for i in range(3))
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = c
    sheen = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sheen)
    sd.ellipse([90, 430, 1190, 640], fill=34)
    sheen = sheen.filter(ImageFilter.GaussianBlur(60))
    bg = ImageChops.add(bg, Image.merge(
        "RGB", (sheen, sheen, sheen.point(lambda v: int(v * 0.9)))))
    return bg


BG = make_bg()
