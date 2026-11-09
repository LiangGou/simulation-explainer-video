#!/usr/bin/env python3
"""ARCHETYPE — accumulator_scale: two running totals on a balance.

A sim accumulates values into two pans; the scale draws the totals,
tilts by their difference, and turns green at equality. The numbers on
the pans are the sim's — the choreography passes step["L"], step["R"],
never literals.

  Worked example (Turing episode): the partition machine guesses each
  of ten numbers into the left or right pile. Mid-run the scale reads
  103 vs 56; at the end it reads 254 = 254 and turns green. The
  narration says "左边，二百五十四；右边，二百五十四" — and QA
  ASR-checks exactly those spoken numbers against this sim.

Origin: generalized from the Turing build (sims.py draw_scale +
partition_sim).
"""
import math

from engine.stage import *


class TwoPanAccumulator:
    """Running totals for a sequence of (side, value) choices.
    steps() returns one dict per choice with the totals AFTER it —
    feed frame i from steps[i], so the scale can never run ahead of
    or behind the choices the audience has seen."""

    def __init__(self, choices):
        self.choices = list(choices)  # [(side, value)], side in "L"/"R"

    def steps(self):
        out = []
        L = R = 0
        for i, (side, v) in enumerate(self.choices):
            if side == "L":
                L += v
            else:
                R += v
            out.append({"i": i, "side": side, "value": v, "L": L, "R": R})
        return out

    @property
    def totals(self):
        s = self.steps()
        return (s[-1]["L"], s[-1]["R"]) if s else (0, 0)


def draw_scale(d, glow, cx, top_y, left_val, right_val, tilt=None,
               green=False, scale=1.0, show_vals=True, pan_cards=None):
    """Draw the brass balance. left_val/right_val accept floats so the
    choreography can ease between two sim steps (the displayed number
    is rounded; the tilt follows the true difference). pan_cards:
    ([left card labels], [right card labels]) drawn as mini cards
    standing on each pan."""
    s = scale
    if tilt is None:
        tilt = clamp((right_val - left_val) / 220.0, -1, 1) * 0.10
    beam = 400 * s
    post_h = 168 * s
    base_y = top_y + post_h + 58 * s
    d.ellipse([cx - 52 * s, base_y - 8 * s, cx + 52 * s, base_y + 10 * s],
              outline=BRASS, width=3)
    pivot_y = top_y + 14 * s
    d.line([cx, pivot_y, cx, base_y - 4 * s], fill=BRASS, width=int(6 * s))
    lx, rx = cx - beam / 2, cx + beam / 2
    ly = pivot_y - (beam / 2) * math.sin(tilt)
    ry = pivot_y + (beam / 2) * math.sin(tilt)
    d.line([lx, ly, rx, ry], fill=BRASS, width=int(6 * s))
    d.ellipse([cx - 7 * s, pivot_y - 7 * s, cx + 7 * s, pivot_y + 7 * s],
              fill=GOLD_L, outline=BRASS_D, width=1)
    num_col = GREEN if green else WHITE
    for side, (ex, ey, val) in enumerate(((lx, ly, left_val),
                                          (rx, ry, right_val))):
        pan_y = ey + 74 * s
        d.line([ex, ey, ex - 44 * s, pan_y], fill=BRASS,
               width=max(1, int(2 * s)))
        d.line([ex, ey, ex + 44 * s, pan_y], fill=BRASS,
               width=max(1, int(2 * s)))
        d.line([ex, ey, ex, pan_y], fill=BRASS, width=max(1, int(2 * s)))
        if pan_cards:
            cards = pan_cards[side]
            cw, chh = 23 * s, 16 * s
            total_w = len(cards) * (cw + 2 * s)
            sx = ex - total_w / 2
            for k, num in enumerate(cards):
                kx = sx + k * (cw + 2 * s)
                ky = pan_y - chh + 2 * s
                d.rounded_rectangle([kx, ky, kx + cw, ky + chh], radius=2,
                                    fill=PAPER, outline=BRASS_D, width=1)
                text_c(d, kx + cw / 2, ky + 1, str(num), F(SERIF, 11 * s), INK)
        d.polygon([(ex - 58 * s, pan_y), (ex + 58 * s, pan_y),
                   (ex + 38 * s, pan_y + 20 * s), (ex - 38 * s, pan_y + 20 * s)],
                  fill=mix(BRASS, (30, 32, 38), 0.25), outline=BRASS_D,
                  width=2)
        if show_vals:
            text_c(d, ex, pan_y + 30 * s, str(int(round(val))),
                   F(SERIFB, 34 * s), num_col)
    if green:
        glow.ellipse([cx - 16, top_y - 4, cx + 16, top_y + 28],
                     fill=(30, 120, 70))
        d.ellipse([cx - 7, top_y + 3, cx + 7, top_y + 17], fill=GREEN)
