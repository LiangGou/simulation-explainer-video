#!/usr/bin/env python3
"""ARCHETYPE — weighted_mix: one source attends to many targets.

Nodes in a row; arcs from the source to each target with thickness
proportional to a weight; the weights are normalized by the sim into
shares (percentages); value color then flows BACK along the arcs and
the source node's color blends toward the weighted mixture. Nothing
is decorative: arc thickness, the percentage labels, and the final
blend color are all computed from the same weight dict.

  Worked example (attention PoC, the pattern's origin): the token
  "it" attends to the sentence "the animal didn't cross the street
  because it was too tired". Weights {animal: .62, tired: .14,
  street: .09, cross: .06, ...} come from a small real scoring pass;
  the animal arc is a thick white-cored cable, the 1% arcs are
  hairlines, and after the flow-back the "it" card is visibly dyed
  62% of the way toward gold — the audience SEES the weighted sum.

Use for: attention, mixture models, weighted voting, Bayesian
updating, any "many inputs, one mixture" beat.

Origin: generalized from the attention PoC renderer (arc_points /
arc_height / draw-on with travelling dot / value flow + blend).
"""
import math

from engine.stage import *


class WeightedMix:
    """weights: {target_key: raw_score}. shares() normalizes them.
    The choreography must display shares() — never the raw dict
    re-typed into a label."""

    def __init__(self, weights):
        self.weights = dict(weights)
        tot = sum(self.weights.values())
        if tot <= 0:
            raise ValueError("weights must sum to a positive number")
        self._shares = {k: v / tot for k, v in self.weights.items()}

    def shares(self):
        return dict(self._shares)

    def blend(self, colors, base):
        """Weighted color mixture: colors {key: rgb}, base rgb.
        Returns base moved toward sum(share_k * color_k)."""
        out = list(base)
        for i in range(3):
            target = sum(self._shares[k] * colors[k][i] for k in colors)
            out[i] = int(round(target))
        return tuple(out)


def arc_points(x0, y0, x1, y1, h, n=120):
    """Cubic bezier arc from (x0, y0) up over to (x1, y1)."""
    pts = []
    c1 = (x0, y0 - h)
    c2 = (x1, y1 - h)
    for i in range(n + 1):
        u = i / n
        v = 1 - u
        x = v ** 3 * x0 + 3 * v * v * u * c1[0] + 3 * v * u * u * c2[0] + u ** 3 * x1
        y = v ** 3 * y0 + 3 * v * v * u * c1[1] + 3 * v * u * u * c2[1] + u ** 3 * y1
        pts.append((x, y))
    return pts


def arc_height(x0, x1, w):
    """Heavier weights fly higher — the eye reads importance before
    any label appears."""
    return 46 + abs(x1 - x0) * 0.16 + w * 130


def _partial(pts, p):
    if p <= 0:
        return []
    if p >= 1:
        return pts
    k = max(2, int(len(pts) * p))
    return pts[:k]


def draw_mix_arcs(d, glow, src_xy, targets, mix, progress,
                  flow_phase=None, accent=(53, 224, 208)):
    """Draw the arc fan.

    targets: {key: (x, y)} anchor points (usually node tops).
    progress: {key: 0..1} draw-on progress per arc.
    flow_phase: if not None (0..1 repeating), gold dots travel from
    each major target BACK to the source along its arc — the value
    flow. Only arcs with share >= 0.09 get the white core and the
    flow dots; hairlines stay hairlines.
    """
    sx, sy = src_xy
    shares = mix.shares()
    for key, (tx, ty) in targets.items():
        w = shares[key]
        p = progress.get(key, 0.0)
        if p <= 0:
            continue
        h = arc_height(sx, tx, w)
        pts = arc_points(sx, sy, tx, ty, h)
        pp = _partial(pts, p)
        aw = 1.2 + w * 13.5
        # glow pass: fat soft underlay
        if len(pp) >= 2:
            glow.line(pp, fill=tuple(int(c * 0.55) for c in accent),
                      width=int(aw + 3.5), joint="curve")
            d.line(pp, fill=accent, width=max(1, int(round(aw))),
                   joint="curve")
            if w >= 0.09:
                d.line(pp, fill=(215, 255, 250),
                       width=max(1, int(round(aw * 0.35))), joint="curve")
        # travelling dot at the pen tip while drawing on
        if p < 1.0 and pp:
            dx, dy = pp[-1]
            glow.ellipse([dx - 6, dy - 6, dx + 6, dy + 6],
                         fill=(190, 255, 248))
        # value flow back to source
        if flow_phase is not None and w >= 0.09 and p >= 1.0:
            for k in range(3):
                u = (flow_phase + k / 3.0) % 1.0
                pos = pts[int((1 - u) * (len(pts) - 1))]
                rr = 6 if w >= 0.3 else 4.5
                glow.ellipse([pos[0] - rr, pos[1] - rr,
                              pos[0] + rr, pos[1] + rr],
                             fill=(255, 214, 130))
                d.ellipse([pos[0] - 3.4, pos[1] - 3.4,
                           pos[0] + 3.4, pos[1] + 3.4],
                          fill=(255, 230, 170))
    return shares


def draw_share_label(d, xy, share, progress=1.0, min_share=0.09):
    """Orange percentage label at an arc apex, counted up by
    `progress` (the number on screen is share * progress, so it
    lands exactly on the sim's share)."""
    if share < min_share:
        return
    val = share * 100.0 * progress
    if val < 0.6:
        return
    x, y = xy
    d.text((x - 26, y - 44), f"{int(round(val))}%",
           font=F(SANSB, 30), fill=ORANGE)
