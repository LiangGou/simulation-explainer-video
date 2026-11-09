#!/usr/bin/env python3
"""ARCHETYPE — containment_stage: a big set as a physical platform,
the subset as a smaller platform standing on it, members as signposts.

Containment is spatial, not a Venn diagram drawn with a compass: the
subset platform sits ON the set platform, member signposts are stuck
into whichever region they belong to, and a side panel can carry a
mini-diagram (a tree, a path) that glosses the picture.

  Worked example (Turing episode, segment S9 — the signature frame):
  the purple NP platform holds signposts 等和划分？ / 数独？ / 扫雷？ /
  分解因数 (gold question marks — membership suspected, not proven);
  the cyan P platform inside it holds 求和 / 找最小 / 排序 plus the
  conch prop and a mini tape; the left panel shows a straight path
  labelled ≤p(n) beside a branching tree. The narration only has to
  say "P 的问题全都在 NP 里面" — the stage already showed it.

Origin: generalized from the Turing build (sims.py draw_signpost;
render.py shot_S9 platform + choice-tree panel).
"""
from engine.stage import *


def draw_platform_disc(d, x, y, w, h, rim, top, inner):
    """One 2.5D platform: a dropped rim ellipse, a top ellipse, and a
    lighter inner field. Signposts plant at y positions inside the
    top ellipse."""
    d.ellipse([x, y + h * 0.045, x + w, y + h * 0.045 + h * 0.955],
              fill=rim)
    d.ellipse([x, y, x + w, y + h], fill=top)
    ix, iy = w * 0.045, h * 0.06
    d.ellipse([x + ix, y + iy, x + w - ix, y + h - iy * 0.4], fill=inner)


def draw_signpost(d, x, y_base, text, s=1.0, qmark=False, sub=None):
    """A paper sign on a brass post. qmark plants the gold "?" of an
    unproven member; sub is a small caption under the sign (e.g. the
    integer 8616460799 under 分解因数 in the Turing episode)."""
    pw = (len(text) * 27 + 26) * s
    ph = 42 * s
    top = y_base - 92 * s
    d.line([x, y_base, x, top + ph], fill=BRASS, width=max(2, int(5 * s)))
    d.ellipse([x - 4 * s, y_base - 3 * s, x + 4 * s, y_base + 3 * s],
              fill=BRASS_D)
    d.rounded_rectangle([x - pw / 2, top, x + pw / 2, top + ph],
                        radius=5 * s, fill=PAPER, outline=BRASS_D, width=2)
    text_c(d, x, top + (ph - 26 * s) / 2 - 2, text, F(CJKB, 24 * s), INK)
    if sub:
        text_c(d, x, top + ph + 2, sub, F(SERIF, 14 * s), DIMTXT)
    if qmark:
        text_c(d, x + pw / 2 - 8 * s, top - 34 * s, "?", F(SERIFB, 30 * s),
               GOLD_L)


def draw_side_panel(d, rect, title, outline=PURPLE, title_color=None):
    """A dark info panel with a title; returns the inner rect for the
    caller's mini-diagram. In the Turing episode this panel holds the
    选择树 (choice tree) gloss: one straight path vs one tree."""
    x0, y0, x1, y1 = rect
    d.rounded_rectangle([x0, y0, x1, y1], radius=12,
                        fill=(13, 14, 24, 235), outline=outline, width=2)
    text_c(d, (x0 + x1) / 2, y0 + 16, title, F(CJKB, 26),
           title_color or PURPLE_L)
    return (x0 + 16, y0 + 52, x1 - 16, y1 - 16)
