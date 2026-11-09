#!/usr/bin/env python3
"""ARCHETYPE — title_card: the thesis statement as a physical event.

Key claims do not appear as subtitles; they land as large centered
typeset cards while the stage dims behind them. Three forms:

  wipe_reveal  — big serif lines revealed left-to-right by a moving
                 mask (Turing S5: "Nondeterministic / Polynomial").
  statement    — a bordered card with a title line and a claim line
                 (Turing S3: the Church–Turing thesis card).
  final_card   — the whole stage dims to near-black and one huge
                 line holds (Turing S10: "P = NP ?" for ~2.8s;
                 attention PoC: "每个词，都在看所有词").

Plus strikethrough(): the joke form — a wrong claim on a paper card,
crossed out in red as the narration corrects it ("NP = Not P").
"""
from PIL import Image, ImageDraw, ImageChops

from engine.stage import *


def wipe_reveal(img, lines, progress, y=218, line_h=78, font_size=58,
                x_center=640):
    """Draw serif lines onto a layer and reveal them with a mask that
    grows with progress (0..1). lines: [(text, font_path), ...]."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    maxw = 0
    for i, (txt, fp) in enumerate(lines):
        f = F(fp, font_size)
        maxw = max(maxw, ld.textlength(txt, font=f))
        text_c(ld, x_center, y + i * line_h, txt, f, WHITE)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    rw = (maxw + 60) * clamp(progress)
    md.rectangle([x_center - (maxw + 60) / 2, y - 28,
                  x_center - (maxw + 60) / 2 + rw,
                  y + line_h * len(lines) + 10], fill=255)
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"),
              (0, 0))
    return img


def statement_card(d, rect, title, body, title_size=32, body_size=23):
    """Bordered thesis card. rect: (x0, y0, x1, y1). Draw it through
    engine.render.fade_in so it arrives instead of popping."""
    x0, y0, x1, y1 = rect
    d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                        fill=(10, 12, 18, 225), outline=GOLD, width=1)
    text_c(d, (x0 + x1) / 2, y0 + 10, title, F(SERIFCJKB, title_size), WHITE)
    text_c(d, (x0 + x1) / 2, y0 + 54, body, F(CJK, body_size), DIMTXT)


def final_card(img, text, progress, font_size=104, dim=205):
    """Dim the stage and hold one huge centered serif line. progress
    drives both the dim and the fade-in of the text."""
    if progress <= 0:
        return img
    ov = Image.new("RGBA", (W, H), (0, 0, 0, int(dim * clamp(progress))))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    f = F(SERIFB, font_size)
    tw = d.textlength(text, font=f)
    d.text(((W - tw) / 2, 296), text, font=f,
           fill=WHITE + (int(255 * clamp(progress)),))
    return img


def strikethrough(d, x0, x1, y, progress, color=RED, width=5):
    """A red line drawn across [x0, x1] at height y as progress runs —
    the visual form of 'no, that's the classic mistake'."""
    if progress <= 0:
        return
    d.line([x0, y, x0 + (x1 - x0) * clamp(progress), y],
           fill=color, width=width)
