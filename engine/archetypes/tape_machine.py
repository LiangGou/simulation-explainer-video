#!/usr/bin/env python3
"""ARCHETYPE — tape_machine: a Turing-style tape + head + delta board.

Parameterized by any delta table and alphabet; contains no episode
content. The sim runs FIRST and returns a step list; every visual
(highlight cell, head position, lamp color, step counter) is read from
that list. This is the pattern's whole point:

  Worked example (Turing episode): the parity machine's delta has
  q0 on "1" -> write 0, move R, go to q1. When the run reaches that
  step, the board highlights row q0 / column "1" — because the step
  dict says so, not because the choreography typed a coordinate.
  If the highlight and the head ever disagree, the sim is wrong,
  and the frame proves it. That is what "working simulation" means.

Origin: generalized from the Turing build (was stage.py draw_tape /
draw_head / draw_counter and sims.py draw_delta_board + parity_tm).
"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from engine.stage import *

LAMP_Q0 = (246, 240, 220)
LAMP_Q1 = (206, 186, 255)
LAMP_ACC = (96, 255, 156)
LAMP_REJ = (255, 110, 96)


class TapeMachine:
    """A deterministic single-tape machine.

    delta: {(state, symbol): (write, "L"/"R", next_state)}
    symbols beyond the input read as `blank`. The run stops when the
    next state is in halt_states (the halting transition is recorded
    as a step but does not move the head and is not `counted` — the
    step counter counts processed tape cells, as in the reference:
    the parity machine processes 7 cells and its counter ends at 7).
    """

    def __init__(self, delta, input_symbols, start_state="q0",
                 blank="⊔", halt_states=("q_acc", "q_rej")):
        self.delta = dict(delta)
        self.input = list(input_symbols)
        self.start_state = start_state
        self.blank = blank
        self.halt_states = tuple(halt_states)

    def run(self):
        tape = list(self.input)
        state, pos, steps = self.start_state, 0, []
        while True:
            sym = tape[pos] if 0 <= pos < len(tape) else self.blank
            w, mv, nxt = self.delta[(state, sym)]
            steps.append({"state": state, "pos": pos, "read": sym,
                          "write": w, "next": nxt,
                          "tape_before": list(tape),
                          "counted": sym != self.blank})
            if 0 <= pos < len(tape):
                tape[pos] = w
            state = nxt
            if state in self.halt_states:
                break
            pos += 1 if mv == "R" else -1
        return steps

    def board_rows(self, states, symbols):
        """Format the delta as board rows:
        [(state, ["w, M, next", ...]), ...] plus index maps."""
        rows = []
        for st in states:
            cells = []
            for sym in symbols:
                if (st, sym) in self.delta:
                    w, mv, nxt = self.delta[(st, sym)]
                    cells.append(f"{w}, {mv}, {nxt}")
                else:
                    cells.append("")
            rows.append((st, cells))
        row_of = {st: i for i, st in enumerate(states)}
        col_of = {sym: i for i, sym in enumerate(symbols)}
        return rows, row_of, col_of


# ---------------------------------------------------------------- drawing
def draw_tape(d, x0, y, cells, cell_w=78, cell_h=56, font_size=30,
              n_show=None, sym_colors=None, cell_fill=None):
    """Draw a tape row. cells beyond n_show render as dark blanks;
    two faded extension cells are drawn on each side."""
    f = F(SERIF, font_size)
    centers = []
    for k in range(-2, 0):
        x = x0 + k * cell_w
        d.rounded_rectangle([x + 2, y, x + cell_w - 2, y + cell_h], radius=4,
                            fill=mix(PAPER, (20, 26, 38), 0.55),
                            outline=mix(BRASS_D, (20, 26, 38), 0.4), width=1)
    n = len(cells) if n_show is None else min(len(cells), n_show)
    for i in range(len(cells)):
        x = x0 + i * cell_w
        cx = x + cell_w / 2
        centers.append((cx, x))
        if i >= n:
            continue
        fill = PAPER if cell_fill is None else cell_fill(i)
        d.rounded_rectangle([x + 2, y, x + cell_w - 2, y + cell_h], radius=4,
                            fill=fill, outline=BRASS_D, width=2)
        d.line([x + 4, y + 3, x + cell_w - 4, y + 3],
               fill=mix(fill, WHITE, 0.5), width=1)
        s = cells[i]
        if s:
            col = INK if sym_colors is None else sym_colors(i, s)
            tw = d.textlength(s, font=f)
            d.text((cx - tw / 2, y + (cell_h - font_size) / 2 - 3), s,
                   font=f, fill=col)
    x_end = x0 + len(cells) * cell_w
    for k in range(3):
        x = x_end + k * cell_w
        if x > W - 10:
            break
        d.rounded_rectangle([x + 2, y, x + cell_w - 2, y + cell_h], radius=4,
                            fill=mix(PAPER, (20, 26, 38), 0.55),
                            outline=mix(BRASS_D, (20, 26, 38), 0.4), width=1)
    return centers


def draw_head(img, d, cx, tape_y, state, lamp=(240, 200, 110),
              scale=1.0, bob=0.0):
    """The brass read/write head with a state lamp. Lamp color encodes
    state at a glance (warm white q0, violet q1, green accept, red
    reject in the Turing episode) — pass LAMP_* or your own."""
    s = scale
    bw, bh = 92 * s, 58 * s
    x0, x1 = cx - bw / 2, cx + bw / 2
    y1 = tape_y - 6 * s + bob
    y0 = y1 - bh
    lamp_cy = y0 - 12 * s
    r = 13 * s
    gr = int(r * 3.4)
    gx0, gy0 = max(0, int(cx - gr)), max(0, int(lamp_cy - gr))
    gx1, gy1 = min(W, int(cx + gr)), min(H, int(lamp_cy + gr))
    if gx1 > gx0 and gy1 > gy0:
        patch = Image.new("RGB", (gx1 - gx0, gy1 - gy0), (0, 0, 0))
        pd = ImageDraw.Draw(patch)
        pd.ellipse([cx - r * 2.1 - gx0, lamp_cy - r * 2.1 - gy0,
                    cx + r * 2.1 - gx0, lamp_cy + r * 2.1 - gy0],
                   fill=tuple(int(c * 0.55) for c in lamp))
        patch = patch.filter(ImageFilter.GaussianBlur(9))
        region = img.crop((gx0, gy0, gx1, gy1))
        img.paste(ImageChops.add(region, patch), (gx0, gy0))
        d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - 52 * s, tape_y + 2, cx + 52 * s, tape_y + 12 * s],
              fill=(8, 10, 14))
    d.rounded_rectangle([x0, y0, x1, y1], radius=8 * s, fill=BRASS,
                        outline=BRASS_D, width=2)
    d.rounded_rectangle([x0 + 7 * s, y0 + 7 * s, x1 - 7 * s, y1 - 16 * s],
                        radius=5 * s, fill=mix(BRASS, GOLD_L, 0.45))
    d.polygon([(cx - 9 * s, y1), (cx + 9 * s, y1), (cx, y1 + 12 * s)],
              fill=BRASS_D)
    d.rectangle([cx - 3 * s, lamp_cy + 6 * s, cx + 3 * s, y0], fill=BRASS_D)
    d.ellipse([cx - r, lamp_cy - r, cx + r, lamp_cy + r], fill=lamp,
              outline=mix(lamp, WHITE, 0.35), width=2)
    d.ellipse([cx - r * 0.38, lamp_cy - r * 0.52, cx + r * 0.1,
               lamp_cy - r * 0.05], fill=mix(lamp, WHITE, 0.75))
    f = F(SERIF, 30 * s)
    col = lamp if state in ("q_acc", "q_rej") else (235, 238, 240)
    d.text((cx + r + 10 * s, lamp_cy - 17 * s), state, font=f, fill=col)


def draw_counter(d, x, y, value, w=150, h=118, label="步 数"):
    """A brass mechanical step counter. The value is whatever the sim
    says it is this frame — feed it len(processed steps), never a
    literal from the script."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=BRASS,
                        outline=BRASS_D, width=2)
    d.rounded_rectangle([x + 12, y + 12, x + w - 12, y + 62], radius=5,
                        fill=(16, 17, 20), outline=BRASS_D, width=1)
    text_c(d, x + w / 2, y + 16, str(value), F(SERIFB, 38), (245, 240, 220))
    text_c(d, x + w / 2, y + 74, label, F(CJKB, 24), (52, 42, 20))
    d.ellipse([x + w / 2 - 9, y - 12, x + w / 2 + 9, y + 4], fill=BRASS_D)


def draw_delta_board(d, x, y, w, title, rows, highlight=None,
                     hl_color=GOLD, extra_hl=None, cell_h=54, font_size=21,
                     title_size=23, cols=("0", "1", "⊔"), cell_font=None,
                     lab_w=52):
    """The rule-table blackboard on its brass stand. `highlight` is a
    (row, col) tuple — in an episode it is ALWAYS derived from the
    current sim step: highlight=(row_of[step.state], col_of[step.read]).
    extra_hl maps (row, col) -> color for secondary marks (e.g. the
    green accept cell after halting, the red reject cell flashing the
    road not taken). Returns the board height."""
    col_w = (w - lab_w) / 3.0
    head_h = 40
    h = head_h + cell_h * len(rows) + 58
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=(15, 17, 23),
                        outline=GOLD, width=3)
    d.rounded_rectangle([x + 5, y + 5, x + w - 5, y + h - 5], radius=6,
                        outline=BRASS_D, width=1)
    text_c(d, x + w / 2, y + 10, title, F(CJK, title_size), (238, 240, 244))
    gy = y + 48
    f_h = F(SERIF, 22)
    d.text((x + 14, gy), "δ", font=f_h, fill=DIMTXT)
    for j, cname in enumerate(cols):
        text_c(d, x + lab_w + (w - lab_w) * (j + 0.5) / 3.0, gy, cname,
               f_h, DIMTXT)
    d.line([x + 12, gy + 30, x + w - 12, gy + 30], fill=BRASS_D, width=1)
    f_lab = F(SERIF, 22)
    f_cell = cell_font if cell_font is not None else F(SERIF, font_size)
    for r, (lab, cells) in enumerate(rows):
        cy = gy + 38 + r * cell_h
        if r > 0:
            d.line([x + 12, cy - 4, x + w - 12, cy - 4],
                   fill=(60, 58, 50), width=1)
        text_c(d, x + lab_w / 2 + 4, cy + cell_h / 2 - 14, lab, f_lab,
               (238, 240, 244))
        for c in range(3):
            cx0 = x + lab_w + c * col_w
            if c > 0:
                d.line([cx0, cy, cx0, cy + cell_h - 8],
                       fill=(60, 58, 50), width=1)
            hl = None
            if highlight == (r, c):
                hl = hl_color
            if extra_hl and (r, c) in extra_hl:
                hl = extra_hl[(r, c)]
            if hl is not None:
                d.rounded_rectangle([cx0 + 4, cy + 2, cx0 + col_w - 4,
                                     cy + cell_h - 6], radius=5,
                                    fill=tuple(int(v * 0.30) for v in hl),
                                    outline=hl, width=2)
            if cells[c]:
                text_c(d, cx0 + col_w / 2, cy + cell_h / 2 - 14, cells[c],
                       f_cell, (225, 229, 235))
    d.polygon([(x + w / 2 - 10, y + h), (x + w / 2 + 10, y + h),
               (x + w / 2 + 26, y + h + 22), (x + w / 2 - 26, y + h + 22)],
              fill=BRASS_D)
    d.ellipse([x + w / 2 - 34, y + h + 18, x + w / 2 + 34, y + h + 30],
              fill=BRASS_D)
    return h


def board_cell_rect(x, y, w, r, c, cell_h=54, lab_w=52):
    """Pixel rect of board cell (r, c) — for overlays that redraw one
    cell (e.g. a two-rule nondeterministic cell)."""
    col_w = (w - lab_w) / 3.0
    cx0 = x + lab_w + c * col_w
    cy = y + 48 + 38 + r * cell_h
    return (cx0 + 4, cy + 2, cx0 + col_w - 4, cy + cell_h - 6)
