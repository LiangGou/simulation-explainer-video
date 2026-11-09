#!/usr/bin/env python3
"""ENGINE LAYER — the frame pipeline.

Every frame is drawn in two passes:

  1. a GLOW pass on a black layer (diagram lines, lamp halos, tree
     branches) which is Gaussian-blurred and added to the stage — this
     is what makes thin lines look lit instead of printed;
  2. a SHARP pass for props, text, and state readouts.

Worked example (Turing episode, segment S3): the choreography calls
new_frame(), draws the parity machine's glow into the glow layer,
commit()s it, then draws the tape, head, delta board, and step counter
— whose value it reads from the TapeMachine run, never from a literal.

Camera: episodes get push_in() (center-crop zoom) as the one camera
transform. The reference videos move the camera instead of cutting;
a slow 1.00 -> 1.045 push across a held shot is the standard move.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from engine.stage import W, H, BG
from engine.subs import draw_subtitle, subtitle_at


def new_frame():
    """Return (image, glow_layer, glow_draw). Start every scene here."""
    img = BG.copy()
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    return img, glow, ImageDraw.Draw(glow)


def commit(img, glow):
    """Composite the blurred glow layer onto the image.
    Returns (image, sharp_draw) for the second pass."""
    img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(6)))
    return img, ImageDraw.Draw(img, "RGBA")


def glyph_tile(sym, font, color):
    """A single glyph on a transparent tile — used for flip animations
    (a tape symbol squashing vertically as it is rewritten)."""
    t = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    td = ImageDraw.Draw(t)
    td.text((32, 30), sym, font=font, fill=color + (255,), anchor="mm")
    return t


def fade_in(base, draw_fn, a):
    """Draw draw_fn onto a fresh layer and alpha-composite at strength
    a (0..1). Used for boards, cards, and panels entering the stage.
    Mutates base in place, like the original pipeline."""
    if a <= 0.001:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    draw_fn(ld)
    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    base.paste(Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB"),
               (0, 0))


def push_in(img, z):
    """Center-crop zoom by factor z (the stage camera's only move)."""
    if z <= 1.001:
        return img
    cw, chh = int(W / z), int(H / z)
    x0, y0 = (W - cw) // 2, (H - chh) // 2
    crop = img.crop((x0, y0, x0 + cw, y0 + chh))
    return crop.resize((W, H), Image.BICUBIC)


def render_episode_frame(episode, seg_id, u, ctx):
    """Render one frame of an episode segment at local time u:
    the scene's choreography, then the scheduled subtitle on top."""
    img = episode.SCENES[seg_id](u, ctx)
    cues = getattr(episode, "SUBS", {}).get(seg_id)
    if cues:
        sub = subtitle_at(cues, u, ctx["A"], ctx["a"])
        if sub:
            d = ImageDraw.Draw(img, "RGBA")
            draw_subtitle(d, sub)
    return img
