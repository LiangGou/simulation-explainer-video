#!/usr/bin/env python3
"""ARCHETYPE — branching_tree: a choice tree with one winning path.

The tree grows level by level; exactly one root-to-leaf path lights
green, the rest dim. The green path is DATA (a tuple of "L"/"R"), and
in an honest episode it is the path the episode's sim actually took:

  Worked example (Turing episode): the partition machine's winning
  assignment R L L R R R L L R L, read as tree turns, is the green
  path in segment S7 — the audience watches the one branch, out of
  2^10, that the machine "guessed" correctly. In S7B the same tree
  carries the accounting: 10 guesses + 9 checks = 19 steps down the
  green path, versus 1024 x 9 = 9216 for exhaustive search.

Origin: generalized from the Turing build (sims.py tree_layout /
draw_tree).
"""
import math

from engine.stage import *


def tree_layout(cx, y0, depth, dx0, dy):
    """Positions for a full binary tree. Keys are path tuples:
    () is the root, ("L", "R") is left-then-right, etc."""
    pos = {}

    def rec(path, x, y, dx):
        pos[path] = (x, y)
        if len(path) < depth:
            rec(path + ("L",), x - dx, y + dy, dx / 2)
            rec(path + ("R",), x + dx, y + dy, dx / 2)

    rec((), cx, y0, dx0)
    return pos


def draw_tree(d, glow, pos, depth, grow_levels, green_path=(),
              node_r=7, base_col=PURPLE, dim_rest=0.0):
    """grow_levels is a float: 2.5 means two levels fully grown and
    the third halfway (edges draw on). green_path: the winning path
    tuple; pass () for no winner yet. dim_rest (0..1) fades every
    non-winning branch toward the background once the winner is lit."""
    for lv in range(depth):
        p = clamp(grow_levels - lv)
        if p <= 0:
            continue
        for path, (x, y) in pos.items():
            if len(path) != lv:
                continue
            for ch in ("L", "R"):
                cpath = path + (ch,)
                if cpath not in pos:
                    continue
                cx2, cy2 = pos[cpath]
                on_green = len(green_path) > 0 and green_path[:len(cpath)] == cpath
                col = GREEN if on_green else base_col
                ex = lerp(x, cx2, p)
                ey = lerp(y, cy2, p)
                if dim_rest and not on_green:
                    col = mix(col, (40, 44, 54), dim_rest)
                wd = 4 if on_green else 2
                if on_green:
                    glow.line([x, y, ex, ey], fill=(20, 90, 55), width=7)
                d.line([x, y, ex, ey], fill=col, width=wd)
    for path, (x, y) in pos.items():
        if len(path) > math.ceil(grow_levels):
            continue
        on_green = len(green_path) > 0 and green_path[:len(path)] == path
        col = GREEN if on_green else PURPLE_L
        if dim_rest and not on_green:
            col = mix(col, (52, 56, 68), dim_rest)
        d.ellipse([x - node_r, y - node_r, x + node_r, y + node_r], fill=col)
