#!/usr/bin/env python3
"""EPISODE LAYER — turing-machine-np (worked example).

An emulation of one segment of the explainer video 《这可能是人类提出最深刻的数学/计算机问题》
by 漫士沉思录 (Lu Rui): the beat that defines the Turing machine and NP.
This module is the EPISODE CONTRACT in action — everything episode-
specific lives here and only here:

  * SEGMENTS   narration chunks (the locked script, TTS-sized)
  * SUBS       subtitle cue splits per segment
  * the sims   parity machine + partition machine, defined as data on
               the engine's archetypes (TapeMachine, TwoPanAccumulator)
  * SCENES     this episode's shot choreography glue: when things
               enter, where labels sit, which sim step drives which
               frame. One-off props (the magic conch) live here too —
               per the growth discipline, a shape needed once stays in
               the episode layer.

The engine renders this folder exactly like any other episode:
  python3 -m engine.synth examples/turing-machine-np   (audio, once)
  python3 -m engine.build examples/turing-machine-np stills
  python3 -m engine.build examples/turing-machine-np
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageChops

from engine.stage import *
from engine.render import new_frame, commit, glyph_tile, fade_in
from engine.archetypes.tape_machine import (
    TapeMachine, draw_tape, draw_head, draw_counter,
    draw_delta_board, board_cell_rect,
    LAMP_Q0, LAMP_Q1, LAMP_ACC, LAMP_REJ)
from engine.archetypes.accumulator_scale import (
    TwoPanAccumulator, draw_scale)
from engine.archetypes.branching_tree import tree_layout, draw_tree
from engine.archetypes.containment_stage import draw_signpost

EPISODE_ID = "turing-machine-np"
VOICE = "avocado_v2:MAI_01"   # Aria — the episode's pinned narrator
LANG = "zh"
OUTPUT_NAME = "turing-segment-v1.mp4"

# QA harness data (engine/qa.py): segments whose audio carries numbers,
# and every spoken number with its accepted transcript spellings.
ASR_FILES = ["s3", "s6", "s7b"]
EXPECTED_NUMBERS = {
    "1024": ["1024", "一千零二十四"],
    "9216": ["9216", "九千二百一十六"],
    "19": ["19", "十九"],
    "2n": ["2n", "二千", "两倍"],
    "254": ["254", "二百五十四"],
    "508": ["508", "五百零八"],
    "7steps": ["七步", "7步"],
}

# ============================== narration chunks (locked script) ==============================
SEGMENTS = {
 "S1": ["但检查到底是什么意思？快，又到底有多快？",
        "要把这两个词说准确，我们得回来认识一位老朋友——图灵机。"],
 "S2": ["它有一条无限长的纸带，分成一个个格子，每格写着一个符号。",
        "纸带上方悬着一个读写头，能读当前格子的符号，能改写它，还能向左或向右移动一格。",
        "而读写头内部，还记着一个状态。"],
 "S3": ["它每走一步，先看状态，再看读到的符号，然后查一张表：这个组合之下，该写什么、往哪边移、切换到什么状态。",
        "这台机器要判断的，是纸带上 1 的个数，是不是偶数。",
        "规则只有两条：读到 1，就把它改写成 0，同时换一个状态；读到 0，原样通过，状态不变。",
        "七步之后，读写头停在一个空格上——状态是 q0，它进入接受。",
        "接受，意味着它判断：有解；拒绝，意味着：无解。",
        "而我们今天写的任何一个程序，都能改写成这样一台图灵机。这句话有个名字，叫丘奇-图灵论题。"],
 "S4": ["注意看，在这台普通的图灵机里，状态和符号一旦定下来，下一步该做什么，有且只有一条规则。",
        "这叫确定性。它像一条单行道，从头走到尾，没有岔路。"],
 "S5": ["现在，想象一种神奇的图灵机。同一个状态，读到同一个符号，它面前可以有好几条规则，每条都合法。",
        "这就是非确定性图灵机。",
        "NP 里的那个 N，nondeterministic，意思就是非确定性——不是 not P，别闹这个经典笑话。"],
 "S6": ["还记得那十个数字，分成两堆的问题吗？",
        "56、19、84、29、93、16、78、22、60、51，总和，五百零八。",
        "非确定性机器解它，分成两段。第一段，它从左到右扫过每一个数字。",
        "每到一个数字，读写头的上方，就会浮现出两个选项：进左边那堆，还是进右边那堆——纯靠猜。",
        "而纸带上方悬着一架天平，两堆的和，随着每一次选择，一格一格往上涨。",
        "第二段，它把刚才每一个选择，写成一行 0 和 1 的凭据，再从头到尾，确定地验一遍。",
        "左边，二百五十四；右边，二百五十四。相等——接受。"],
 "S7": ["这就是 NP 最精髓的地方。你可以想象，这台机器揣着一个神奇海螺，每一次选择，都能完美地猜对。",
        "或者想象它在每个岔路口分身：一个变两个，两个变四个，无数个分身同时探索所有的分支——只要有任何一条路最后走进接受，它就接受。"],
 "S7B": ["我们来算一笔账。猜，每个数字选一次，十步。",
         "验，左边加四次，右边加四次，再比较一次，九步。",
         "一共，十九步，不超过 2n。",
         "而一台确定性机器，只能把一千零二十四种分法，一种一种验下去：九千二百一十六步。",
         "十九，对九千二百一十六。这就是未卜先知的大小。"],
 "S8": ["所以你看，答案容易检查，和能被非确定性图灵机快速解决，其实是一回事。",
        "只要有一个快速的检查程序，在它前面加上一段猜答案的环节，拼起来，就是一台非确定性机器。"],
 "S9": ["而 P 里面的问题，全都在 NP 里面。因为一台确定性机器，本来就可以看成是一台拥有神奇海螺、但从来不用的非确定性机器。",
        "不用猜，都能快速解出来，那当然更算数。"],
 "S10": ["于是，这个困扰了人类五十多年的问题，终于可以一字不差地问出来了：",
         "一切能快速检查答案的问题，是不是也都能快速找到答案本身？",
         "一台平庸的、一步一步的确定性图灵机，到底能不能比肩那台开挂的机器？"],
}

# ============================== subtitle cues ==============================
SUBS = {
 "S1": ["但“检查”到底是什么意思？", "“快”，又到底有多快？",
        "要把这两个词说准确", "我们得回来认识一位老朋友", "图灵机"],
 "S2": ["它有一条无限长的纸带", "分成一个个格子", "每格写着一个符号",
        "纸带上方悬着一个读写头", "能读当前格子的符号", "能改写它",
        "还能向左或向右移动一格", "而读写头内部", "还记着一个状态"],
 "S3": ["它每走一步", "先看状态，再看读到的符号", "然后查一张表",
        "这个组合之下", "该写什么、往哪边移", "切换到什么状态",
        "这台机器要判断的", "是纸带上 1 的个数", "是不是偶数",
        "规则只有两条", "读到 1，就把它改写成 0", "同时换一个状态",
        "读到 0，原样通过，状态不变", "七步之后", "读写头停在一个空格上",
        "状态是 q0，它进入接受", "接受，意味着它判断：有解",
        "拒绝，意味着：无解", "而我们今天写的任何一个程序",
        "都能改写成这样一台图灵机", "这句话有个名字", "叫丘奇-图灵论题"],
 "S4": ["注意看", "在这台普通的图灵机里", "状态和符号一旦定下来",
        "下一步该做什么", "有且只有一条规则", "这叫确定性",
        "它像一条单行道", "从头走到尾，没有岔路"],
 "S5": ["现在，想象一种", "神奇的图灵机", "同一个状态", "读到同一个符号",
        "它面前可以有好几条规则", "每条都合法", "这就是非确定性图灵机",
        "NP 里的那个 N", "nondeterministic", "意思就是非确定性",
        "不是 not P", "别闹这个经典笑话"],
 "S6": ["还记得那十个数字", "分成两堆的问题吗", "56、19、84、29、93",
        "16、78、22、60、51", "总和，五百零八", "非确定性机器解它",
        "分成两段", "第一段", "它从左到右扫过每一个数字", "每到一个数字",
        "读写头的上方", "就会浮现出两个选项", "进左边那堆，还是进右边那堆",
        "纯靠猜", "而纸带上方悬着一架天平", "两堆的和", "随着每一次选择",
        "一格一格往上涨", "第二段", "它把刚才每一个选择",
        "写成一行 0 和 1 的凭据", "再从头到尾", "确定地验一遍",
        "左边，二百五十四", "右边，二百五十四", "相等——接受"],
 "S7": ["这就是 NP 最精髓的地方", "你可以想象", "这台机器揣着一个神奇海螺",
        "每一次选择", "都能完美地猜对", "或者想象它在每个岔路口分身",
        "一个变两个，两个变四个", "无数个分身", "同时探索所有的分支",
        "只要有任何一条路", "最后走进接受", "它就接受"],
 "S7B": ["我们来算一笔账", "猜，每个数字选一次，十步", "验，左边加四次",
         "右边加四次", "再比较一次，九步", "一共，十九步", "不超过 2n",
         "而一台确定性机器", "只能把一千零二十四种分法", "一种一种验下去",
         "九千二百一十六步", "十九，对九千二百一十六", "这就是“未卜先知”的大小"],
 "S8": ["所以你看", "“答案容易检查”", "和“能被非确定性图灵机", "快速解决”",
        "其实是一回事", "只要有一个快速的检查程序", "在它前面",
        "加上一段猜答案的环节", "拼起来", "就是一台非确定性机器"],
 "S9": ["而 P 里面的问题", "全都在 NP 里面", "因为一台确定性机器",
        "本来就可以看成是", "一台拥有神奇海螺", "但从来不用的", "非确定性机器",
        "不用猜", "都能快速解出来", "那当然更算数"],
 "S10": ["于是", "这个困扰了人类", "五十多年的问题", "终于可以一字不差地",
         "问出来了", "一切能快速检查答案的问题", "是不是也都能",
         "快速找到答案本身", "一台平庸的", "一步一步的确定性图灵机",
         "到底能不能", "比肩那台开挂的机器"],
}
def np_badge(d, x=64, y=30):
    d.ellipse([x, y, x + 56, y + 56], outline=PURPLE_L, width=2)
    for i, (dx, dy) in enumerate(((10, 12), (26, 12), (10, 28), (26, 28))):
        d.rectangle([x + dx, y + dy, x + dx + 9, y + dy + 9],
                    outline=PURPLE_L, width=1)
    d.text((x + 66, y + 8), "NP?", font=F(SERIF, 30), fill=PURPLE_L)

# tape geometry shared by D/E shots
TAPE_Y = 478
CELL_W = 78
TAPE_X0 = 46
VIEW_OFF = 3  # input starts at view cell 3

def cell_cx(i):
    return TAPE_X0 + (VIEW_OFF + i) * CELL_W + CELL_W / 2

def tape_cells(symbols, total=17):
    cells = [""] * total
    for i, s in enumerate(symbols):
        cells[VIEW_OFF + i] = s
    return cells

# ============================== episode sims: the parity machine and the partition machine,
# defined as data on the archetypes. Every number the video shows
# (step counter, scale sums, 19 vs 9216) is computed here.
# ================= parity Turing machine =================
PARITY_DELTA = {
    ("q0", "0"): ("0", "R", "q0"), ("q0", "1"): ("0", "R", "q1"),
    ("q0", "⊔"): ("⊔", "R", "q_acc"),
    ("q1", "0"): ("0", "R", "q1"), ("q1", "1"): ("0", "R", "q0"),
    ("q1", "⊔"): ("⊔", "R", "q_rej"),
}
PARITY_INPUT = ["1", "0", "1", "0", "1", "1", "0"]

# The parity machine is pure DATA on the tape_machine archetype:
# a delta table + an input tape. The archetype runs it; the
# choreography below reads PARITY_STEPS and never re-derives a
# state, a highlight, or a counter value by hand.
PARITY_MACHINE = TapeMachine(PARITY_DELTA, PARITY_INPUT)
PARITY_STEPS = PARITY_MACHINE.run()
PARITY_ROWS, STATE_ROW, SYM_COL = PARITY_MACHINE.board_rows(
    ["q0", "q1"], ["0", "1", "⊔"])

# ================= partition NTM =================
PART_NUMBERS = [56, 19, 84, 29, 93, 16, 78, 22, 60, 51]
PART_CHOICE = ["R", "L", "L", "R", "R", "R", "L", "L", "R", "L"]

def partition_sim():
    # The running sums come from the accumulator_scale archetype;
    # this function only renames its step fields for the choreography.
    acc = TwoPanAccumulator(list(zip(PART_CHOICE, PART_NUMBERS)))
    steps = [{"i": s["i"], "n": s["value"], "choice": s["side"],
              "L": s["L"], "R": s["R"]} for s in acc.steps()]
    bits = "".join("1" if c == "L" else "0" for c in PART_CHOICE)
    L, R = acc.totals
    return {"steps": steps, "bits": bits, "L": L, "R": R,
            "total": sum(PART_NUMBERS)}

PART = partition_sim()

ACC = {"guess": len(PART_NUMBERS),
       "addL": sum(1 for c in PART_CHOICE if c == "L") - 1,
       "addR": sum(1 for c in PART_CHOICE if c == "R") - 1}
ACC["verify"] = ACC["addL"] + ACC["addR"] + 1
ACC["total"] = ACC["guess"] + ACC["verify"]
ACC["det"] = (2 ** len(PART_NUMBERS)) * ACC["verify"]
ACC["twon"] = 2 * len(PART_NUMBERS)

# ============================== episode prop: the magic conch (one-off, stays in the episode)
# ================= conch =================
def draw_conch(d, cx, cy, r, glow_it=0.0, glow_layer=None):
    body = (196, 150, 92)
    dark = (120, 92, 52)
    if glow_it > 0 and glow_layer is not None:
        glow_layer.ellipse([cx - r * 1.6, cy - r * 1.5, cx + r * 1.6, cy + r * 1.5],
                           fill=(int(52 * glow_it), int(42 * glow_it), int(14 * glow_it)))
    d.ellipse([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92], fill=body,
              outline=dark, width=2)
    for k in range(3):
        bx = cx - r * (0.55 + 0.16 * k); by = cy - r * (0.72 - 0.10 * k)
        br = r * (0.20 - 0.035 * k)
        d.ellipse([bx - br, by - br, bx + br, by + br],
                  fill=mix(body, GOLD_L, 0.25), outline=dark, width=1)
    pts = []
    for i in range(90):
        uu = i / 89
        ang = uu * math.pi * 4.6 + 0.6
        rr = r * 0.66 * (1 - uu * 0.82)
        pts.append((cx + rr * math.cos(ang) * 0.95, cy + rr * math.sin(ang) * 0.85))
    d.line(pts, fill=dark, width=max(2, int(r * 0.09)))
    d.ellipse([cx - r * 0.16, cy - r * 0.14, cx + r * 0.30, cy + r * 0.30],
              fill=mix(body, WHITE, 0.35), outline=dark, width=1)

# ============================== shot choreography (this episode's glue)
# ================= S1: tape grows =================
def shot_S1(u, ctx):
    img, glow, gd = new_frame()
    A, a = ctx["A"], ctx["a"]
    rf = 14 * ease_out(seg(u, 0.1, A + a * 0.8))
    lx = 60 + (1220 - 60) * seg(u, 0.1, A + a * 0.5)
    gd.line([60, 548, lx, 548], fill=(24, 90, 96), width=5)
    if rf < 14:
        fx = 70 + int(rf) * 82
        gd.ellipse([fx - 8, 492, fx + 8, 508], fill=(120, 200, 190))
    img, d = commit(img, glow)
    draw_tape(d, 70, 470, [""] * 14, cell_w=82, cell_h=58,
              n_show=int(math.ceil(rf)) if rf > 0 else 0)
    return img

# ================= S2: symbols + head + demos =================
def shot_S2(u, ctx):
    img, glow, gd = new_frame()
    A, b = ctx["A"], ctx["b"]
    b1, b2 = b[1], b[2]
    def cx2(i): return 70 + i * 82 + 41
    head_cx = cx2(3)
    if u > b1 + 4.6:
        off = 0.0
        if u < b1 + 5.6:
            off = 82 * ease_io(seg(u, b1 + 4.6, b1 + 5.6))
        elif u < b1 + 6.6:
            off = 82.0
        elif u < b1 + 7.7:
            off = 82 * (1 - ease_io(seg(u, b1 + 6.6, b1 + 7.7)))
        head_cx = cx2(3) + off
    drop = ease_out(seg(u, b1, b1 + 1.2))
    bob = (1 - drop) * -180
    img, d = commit(img, glow)
    # tape + symbols
    cells = [""] * 14
    flip_w = seg(u, b1 + 3.2, b1 + 4.4)
    flipping = 0 < flip_w < 1
    for i, s in enumerate(PARITY_INPUT):
        if u > A + 0.3 + i * 0.5:
            cells[3 + i] = s
    if flipping:
        cells[3] = ""
    draw_tape(d, 70, 470, cells, cell_w=82, cell_h=58, font_size=30)
    if flipping:
        tile = glyph_tile("1", F(SERIF, 30), INK)
        hh = max(2, int(50 * abs(math.cos(math.pi * flip_w))))
        tile = tile.resize((64, hh))
        img.paste(tile, (int(cx2(3) - 32), int(474 + (50 - hh) / 2)),
                  tile)
        d = ImageDraw.Draw(img, "RGBA")
    # read pulse on cell 3
    if b1 + 1.4 < u < b1 + 3.2:
        pa = 0.55 + 0.45 * math.sin((u - b1) * 9)
        d.rounded_rectangle([70 + 3 * 82 + 1, 469, 70 + 4 * 82 - 1, 529],
                            radius=5, outline=(255, 210, 90, int(200 * pa)),
                            width=3)
    if u >= b1:
        draw_head(img, d, head_cx, 470, "q0", lamp=LAMP_Q0, bob=bob)
        if u > b2:
            # state ring pulse in chunk 2
            rp = 22 + 5 * math.sin((u - b2) * 6)
            lamp_cy = 470 - 6 - 58 - 12
            d.ellipse([head_cx - rp, lamp_cy - rp, head_cx + rp, lamp_cy + rp],
                      outline=GOLD_L + (170,), width=2)
    return img

# ================= S3: parity machine full run =================
BOARD_X, BOARD_Y, BOARD_W = 806, 66, 424

def s3_frame(u, ctx):
    img, glow, gd = new_frame()
    A, b = ctx["A"], ctx["b"]
    R0 = A + 13.0
    CYCLE = 1.25
    halt0 = R0 + 7 * CYCLE
    # --- compute machine state at u ---
    final_tape = ["0"] * 7
    if u < R0:
        tape_syms = list(PARITY_INPUT)
        head_pos = 0.0
        head_state = "q0"
        lamp = LAMP_Q0
        counter = 0
        hl = None
    elif u < halt0:
        k = int((u - R0) / CYCLE)
        p = ((u - R0) - k * CYCLE) / CYCLE
        st = PARITY_STEPS[k]
        tape_syms = list(st["tape_before"])
        if p >= 0.5:
            tape_syms[st["pos"]] = st["write"]
        head_pos = st["pos"] + ease_io(seg(p, 0.5, 1.0))
        head_state = st["state"] if p < 0.75 else st["next"]
        lamp = {"q0": LAMP_Q0, "q1": LAMP_Q1}.get(head_state, LAMP_Q0)
        counter = k + (1 if p > 0.9 else 0)
        hl = (STATE_ROW[st["state"]], SYM_COL[st["read"]])
    else:
        tape_syms = final_tape
        head_pos = 7.0
        hp = seg(u, halt0, halt0 + 1.5)
        head_state = "q_acc" if hp >= 1 else "q0"
        lamp = LAMP_ACC if hp >= 1 else LAMP_Q0
        counter = 7
        hl = None
    head_cx = cell_cx(0) + head_pos * CELL_W
    # head lamp glow needs head drawn after commit; draw head in main pass
    img, d = commit(img, glow)
    np_badge(d, 56, 26)
    # board + counter fade in
    def draw_board(dd):
        extra = {}
        if u >= halt0:
            hp = seg(u, halt0, halt0 + 1.5)
            if hp > 0:
                extra[(0, 2)] = GREEN
            if halt0 + 2.6 < u < halt0 + 3.3:
                extra[(1, 2)] = RED
        draw_delta_board(dd, BOARD_X, BOARD_Y, BOARD_W, "1 的个数是偶数？",
                         PARITY_ROWS, highlight=hl, extra_hl=extra, font_size=19)
    fade_in(img, draw_board, ease_out(seg(u, 0.3, 1.5)))
    d = ImageDraw.Draw(img, "RGBA")
    fade_in(img, lambda dd: draw_counter(dd, 118, 108, counter),
            ease_out(seg(u, 0.3, 1.5)))
    d = ImageDraw.Draw(img, "RGBA")
    draw_tape(d, TAPE_X0, TAPE_Y, tape_cells(tape_syms), cell_w=CELL_W,
              cell_h=56, font_size=30)
    draw_head(img, d, head_cx, TAPE_Y, head_state, lamp=lamp)
    # accept/reject chips during chunk 4
    b4 = ctx["b"][4]
    if u > b4 + 0.3:
        ca = seg(u, b4 + 0.3, b4 + 1.1)
        def chips(dd):
            dd.rounded_rectangle([846, 348, 1036, 394], radius=8,
                                 fill=(16, 34, 24, 235), outline=GREEN, width=2)
            text_c(dd, 941, 358, "q_acc → 接受", F(CJK, 21), GREEN)
            dd.rounded_rectangle([1050, 348, 1240, 394], radius=8,
                                 fill=(34, 18, 16, 235), outline=RED, width=2)
            text_c(dd, 1145, 358, "q_rej → 拒绝", F(CJK, 21), RED)
        fade_in(img, chips, ca)
        d = ImageDraw.Draw(img, "RGBA")
    # thesis card during chunk 5
    b5 = ctx["b"][5]
    if u > b5 + 0.3:
        ca = seg(u, b5 + 0.3, b5 + 1.1)
        y0 = 540 + (1 - ca) * 16
        def card(dd):
            dd.rounded_rectangle([260, y0, 1020, y0 + 94], radius=10,
                                 fill=(10, 12, 18, 225), outline=GOLD, width=1)
            text_c(dd, 640, y0 + 10, "丘奇-图灵论题", F(SERIFCJKB, 32), WHITE)
            text_c(dd, 640, y0 + 54, "任何算法，都能写成一台图灵机",
                   F(CJK, 23), DIMTXT)
        fade_in(img, card, ca)
    return img

# ================= S4: determinism =================
def shot_S4(u, ctx):
    img, glow, gd = new_frame()
    A, b = ctx["A"], ctx["b"]
    lx = 60 + (1220 - 60) * seg(u, b[1], ctx["e"][1])
    gd.line([60, 548, lx, 548], fill=(24, 90, 96), width=5)
    img, d = commit(img, glow)
    np_badge(d, 56, 26)
    draw_delta_board(d, BOARD_X, BOARD_Y, BOARD_W, "1 的个数是偶数？",
                     PARITY_ROWS, highlight=(0, 0), font_size=19)
    # dim everything on the board except the highlighted cell
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rounded_rectangle([BOARD_X + 3, BOARD_Y + 3, BOARD_X + BOARD_W - 3,
                          BOARD_Y + 252 - 3], radius=8, fill=(10, 13, 20, 118))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    r = board_cell_rect(BOARD_X, BOARD_Y, BOARD_W, 0, 0)
    d.rounded_rectangle(list(r), radius=5, fill=(76, 57, 18, 255),
                        outline=GOLD, width=2)
    text_c(d, (r[0] + r[2]) / 2, r[1] + 11, "0, R, q0", F(SERIF, 21),
           (225, 229, 235))
    la = ease_out(seg(u, A + 0.2, A + 1.0))
    fade_in(img, lambda dd: text_c(dd, 200, 92, "确定性", F(SERIFCJKB, 46),
                                   WHITE), la)
    d = ImageDraw.Draw(img, "RGBA")
    draw_tape(d, TAPE_X0, TAPE_Y, tape_cells(PARITY_INPUT),
              cell_w=CELL_W, cell_h=56, font_size=30,
              cell_fill=lambda i: mix(PAPER, (24, 30, 42), 0.30))
    draw_head(img, d, cell_cx(0), TAPE_Y, "q0", lamp=LAMP_Q0)
    return img

# ================= S5: nondeterminism + F card =================
def shot_S5(u, ctx):
    A, b, e = ctx["A"], ctx["b"], ctx["e"]
    b2 = b[2]
    if u >= b2:
        return shot_F(u, ctx)
    img, glow, gd = new_frame()
    # branch arcs glow
    if u > A + 8.5:
        ap = seg(u, A + 8.5, A + 9.5)
        for tx in (191, 797):
            pts = []
            for k in range(41):
                t = k / 40 * ap
                x = lerp(cell_cx(2), tx, t)
                y = 545 + (640 - 545) * t + math.sin(t * math.pi) * 26
                pts.append((x, y))
            if len(pts) > 1:
                gd.line(pts, fill=(70, 55, 130), width=4)
    img, d = commit(img, glow)
    np_badge(d, 56, 26)
    draw_delta_board(d, BOARD_X, BOARD_Y, BOARD_W, "1 的个数是偶数？",
                     PARITY_ROWS, font_size=19, extra_hl={(1, 1): PBLUE} if u > A + 5 else None)
    if u > A + 5:
        r = board_cell_rect(BOARD_X, BOARD_Y, BOARD_W, 1, 1)
        d.rounded_rectangle(list(r), radius=5, fill=(30, 48, 92, 255),
                            outline=PBLUE, width=2)
        text_c(d, (r[0] + r[2]) / 2, r[1] + 3, "0, R, q0", F(SERIF, 16),
               (225, 235, 255))
        text_c(d, (r[0] + r[2]) / 2, r[1] + 25, "1, R, q1", F(SERIF, 16),
               (225, 235, 255))
    dim = seg(u, A + 6, A + 7.5)
    fade_in(img, lambda dd: text_c(dd, 200, 92, "确定性", F(SERIFCJKB, 46),
                                   mix(WHITE, (30, 36, 48), dim * 0.6)), 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    fade_in(img, lambda dd: text_c(dd, 224, 156, "非确定性", F(SERIFCJKB, 46),
                                   PURPLE_L), seg(u, A + 6, A + 7.2))
    d = ImageDraw.Draw(img, "RGBA")
    draw_tape(d, TAPE_X0, TAPE_Y, tape_cells(PARITY_INPUT),
              cell_w=CELL_W, cell_h=56, font_size=30)
    draw_head(img, d, cell_cx(2), TAPE_Y, "q1", lamp=LAMP_Q1)
    # branch tapes
    if u > A + 8.5:
        ba = seg(u, A + 8.5, A + 9.3)
        def branches(dd):
            draw_tape(dd, 110, 600, ["0", "0", "1", "", ""], cell_w=54,
                      cell_h=38, font_size=20)
            draw_tape(dd, 716, 600, ["0", "1", "1", "", ""], cell_w=54,
                      cell_h=38, font_size=20)
        fade_in(img, branches, ba)
        d = ImageDraw.Draw(img, "RGBA")
        slide = ease_io(seg(u, A + 11, A + 13.5))
        lx = 191 + slide * 54
        rx = 797 + slide * 54
        acc = u > A + 14
        draw_head(img, d, lx, 600, "q0", lamp=LAMP_Q0, scale=0.6)
        draw_head(img, d, rx, 600, "q_acc" if acc else "q1",
                  lamp=LAMP_ACC if acc else LAMP_Q1, scale=0.6)
        if acc:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            od.rectangle([90, 585, 420, 660], fill=(8, 10, 14, 110))
            img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
                      (0, 0))
            d = ImageDraw.Draw(img, "RGBA")
    return img

def shot_F(u, ctx):
    img = BG.copy()
    d = ImageDraw.Draw(img, "RGBA")
    b2 = ctx["b"][2]
    # wipe-reveal the two big lines
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    text_c(ld, 640, 218, "Nondeterministic", F(SERIFB, 58), WHITE)
    text_c(ld, 640, 296, "Polynomial", F(SERIFB, 58), WHITE)
    total_w = 880
    rw = total_w * seg(u, b2 + 0.2, b2 + 3.0)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([200, 190, 200 + rw, 380], fill=255)
    la = layer.getchannel("A")
    from PIL import ImageChops as _IC
    layer.putalpha(_IC.multiply(la, mask))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    if u > b2 + 3.2:
        d.rounded_rectangle([468, 428, 812, 502], radius=8, fill=PAPER,
                            outline=BRASS_D, width=2)
        text_c(d, 640, 446, "NP = Not P", F(SERIFB, 38), INK)
        sp = seg(u, b2 + 4.4, b2 + 5.1)
        if sp > 0:
            d.line([486, 466, 486 + (794 - 486) * sp, 466], fill=RED, width=5)
    return img

# ================= S6: partition big machine =================
G_BOARD_X, G_BOARD_Y, G_BOARD_W = 896, 58, 348
G_ROWS = [("q1", ["选 0 → 右", "选 1 → 左", "—"]),
          ("q2", ["逐格加总", "比较两和", "q_acc"])]
NUM_X0, NUM_CW, NUM_Y = 30, 64, 478

def num_cx(i):
    return NUM_X0 + i * NUM_CW + NUM_CW / 2

def shot_S6(u, ctx):
    img, glow, gd = new_frame()
    A, b, e = ctx["A"], ctx["b"], ctx["e"]
    img, d = commit(img, glow)
    np_badge(d, 56, 26)
    # ---- stage timing ----
    run0 = b[3]                      # stage 1 runs across chunks 3-4
    CYC = 1.55
    run_end = run0 + 10 * CYC
    s2_0 = b[5]                      # stage 2 chunk
    # ---- machine state at u ----
    if u < run0:
        done = 0
        cur = -1
        phase = 0.0
        dispL = dispR = 0
    elif u < run_end:
        k = int((u - run0) / CYC)
        phase = ((u - run0) - k * CYC) / CYC
        cur = k
        done = k + (1 if phase > 0.6 else 0)
        prev = PART["steps"][k - 1] if k > 0 else {"L": 0, "R": 0}
        tgt = PART["steps"][k]
        w = ease_io(seg(phase, 0.55, 0.95))
        dispL = lerp(prev["L"], tgt["L"], w)
        dispR = lerp(prev["R"], tgt["R"], w)
    else:
        cur = -1
        phase = 0.0
        done = 10
        dispL, dispR = PART["L"], PART["R"]
    green = u > b[6] + 0.2
    # ---- board ----
    hl = None
    extra = {}
    if b[2] < u < run_end:
        if cur >= 0:
            hl = (0, 0 if PART_CHOICE[cur] == "R" else 1)
        else:
            hl = (0, 0)
    if u >= s2_0:
        hl = (1, 0) if u < s2_0 + 6.4 else (1, 1)
    if green:
        extra[(1, 2)] = GREEN
        hl = None
    def board(dd):
        draw_delta_board(dd, G_BOARD_X, G_BOARD_Y, G_BOARD_W, "等和划分？",
                         G_ROWS, highlight=hl, extra_hl=extra,
                         cols=("0", "1", ""), cell_font=F(CJK, 16),
                         cell_h=50, font_size=16, title_size=21)
    fade_in(img, board, ease_out(seg(u, 0.2, 1.2)))
    d = ImageDraw.Draw(img, "RGBA")
    # ---- scale ----
    tilt = None
    if green:
        tilt = 0.0
    cards = ([st["n"] for st in PART["steps"][:done] if st["choice"] == "L"],
             [st["n"] for st in PART["steps"][:done] if st["choice"] == "R"])
    fade_in(img, lambda dd: draw_scale(dd, gd, 430, 76, dispL, dispR,
                                       tilt=tilt, green=green,
                                       pan_cards=cards if done else None),
            ease_out(seg(u, 0.2, 1.2)))
    d = ImageDraw.Draw(img, "RGBA")
    # ---- numbers tape (type-in during chunk 1) ----
    cells = []
    for i, n in enumerate(PART_NUMBERS):
        cells.append(str(n) if u > b[1] + 0.4 + i * 1.05 else "")
    def cell_fill(i):
        if i < done:
            return mix(PAPER, GOLD_L, 0.18) if PART_CHOICE[i] == "L" \
                else mix(PAPER, PBLUE, 0.20)
        return PAPER
    draw_tape(d, NUM_X0, NUM_Y, cells, cell_w=NUM_CW, cell_h=56, font_size=26,
              cell_fill=cell_fill)
    # choice markers
    for i in range(done):
        col = GOLD if PART_CHOICE[i] == "L" else PBLUE
        d.ellipse([num_cx(i) - 4, NUM_Y + 44, num_cx(i) + 4, NUM_Y + 52],
                  fill=col)
    # ---- bits row (stage 2) ----
    if u > s2_0:
        nbits = 0
        for i in range(10):
            if u > s2_0 + 1.2 + i * 0.58:
                nbits = i + 1
        bits_cells = list(PART["bits"][:nbits]) + [""] * (10 - nbits)
        draw_tape(d, NUM_X0, NUM_Y + 68, bits_cells, cell_w=NUM_CW,
                  cell_h=32, font_size=19,
                  sym_colors=lambda i, s: PURPLE,
                  cell_fill=lambda i: mix(PAPER, PURPLE, 0.13))
    # ---- head ----
    if u > b[2] + 0.4:
        if u < run0:
            hcx = num_cx(0)
            hstate, hlamp = "q1", LAMP_Q1
        elif u < run_end:
            k = int((u - run0) / CYC)
            ph = ((u - run0) - k * CYC) / CYC
            hcx = num_cx(k) + NUM_CW * ease_io(seg(ph, 0.8, 1.0)) \
                if k < 9 else num_cx(9)
            hstate, hlamp = "q1", LAMP_Q1
        elif u < s2_0:
            hcx = num_cx(9)
            hstate, hlamp = "q1", LAMP_Q1
        elif u < s2_0 + 1.0:
            hcx = lerp(num_cx(9), num_cx(0), ease_io(seg(u, s2_0, s2_0 + 1.0)))
            hstate, hlamp = "q2", LAMP_Q0
        else:
            bi = min(9, int((u - s2_0 - 1.2) / 0.58)) if u > s2_0 + 1.2 else 0
            hcx = num_cx(bi)
            hstate, hlamp = "q2", LAMP_Q0
        if green:
            hstate, hlamp = "q_acc", LAMP_ACC
        draw_head(img, d, hcx, NUM_Y, hstate, lamp=hlamp, scale=0.92)
        # option chips during stage-1 choice phase
        if 0 <= cur <= 9 and u < run_end:
            ph = ((u - run0) - cur * CYC) / CYC
            oa = seg(ph, 0.0, 0.25)
            if oa > 0:
                oy = NUM_Y - 138
                chosen = PART_CHOICE[cur]
                for lab, dx, ring, side in (("0", -44, PBLUE, "R"),
                                            ("1", 44, GOLD, "L")):
                    is_ch = chosen == side
                    cxp = hcx + dx
                    rr = 21 * (1.18 if (is_ch and ph > 0.35) else 1.0)
                    fill = ring if (is_ch and ph > 0.35) else (16, 20, 28)
                    d.ellipse([cxp - rr, oy - rr, cxp + rr, oy + rr],
                              fill=fill + (int(235 * oa),),
                              outline=ring + (int(255 * oa),), width=3)
                    text_c(d, cxp, oy - 13, lab, F(SERIFB, 24),
                           (INK if (is_ch and ph > 0.35) else WHITE))
                    text_c(d, cxp, oy + 28, "右" if side == "R" else "左",
                           F(CJK, 14), DIMTXT)
    return img

# ================= S7: conch + branching tree =================
def shot_S7(u, ctx):
    img, glow, gd = new_frame()
    A, b = ctx["A"], ctx["b"]
    pos = tree_layout(640, 330, 4, 250, 74)
    grow = 4 * ease_out(seg(u, b[1] + 0.5, b[1] + 8.5))
    lit = u > b[1] + 9.0
    dim = 0.65 * seg(u, b[1] + 10.0, b[1] + 12.5)
    draw_tree(gd, gd, pos, 4, grow,
              green_path=("L", "R", "L", "R") if lit else (), dim_rest=dim)
    img, d = commit(img, glow)
    glow_it = 0.45 + 0.4 * math.sin(u * 1.7) if u < b[1] else 0.8
    draw_conch(d, 640, 232, 56, glow_it=glow_it, glow_layer=gd)
    # redraw tree sharp on main layer too (glow pass is soft)
    draw_tree(d, gd, pos, 4, grow,
              green_path=("L", "R", "L", "R") if lit else (), dim_rest=dim)
    if lit:
        lx, ly = pos[("L", "R", "L", "R")]
        d.ellipse([lx - 9, ly - 9, lx + 9, ly + 9], fill=LAMP_ACC,
                  outline=WHITE, width=1)
        d.text((lx + 16, ly - 13), "q_acc", font=F(SERIF, 24), fill=GREEN)
    return img

# ================= S7B: accounting =================
def _runs(d, x, y, runs):
    cx = x
    for txt, font, col in runs:
        d.text((cx, y), txt, font=font, fill=col)
        cx += d.textlength(txt, font=font)
    return cx

def _runs_c(d, cx_center, y, runs):
    tot = sum(d.textlength(t, font=f) for t, f, c in runs)
    return _runs(d, cx_center - tot / 2, y, runs)

def shot_S7B(u, ctx):
    img, glow, gd = new_frame()
    A, b = ctx["A"], ctx["b"]
    pos = tree_layout(545, 150, 3, 140, 82)
    grow = 3 * seg(u, A + 1.0, A + 6.0)
    lit = u > A + 6.5
    draw_tree(gd, gd, pos, 3, grow,
              green_path=("R", "L", "R") if lit else (),
              dim_rest=0.5 if lit else 0.0, node_r=6)
    img, d = commit(img, glow)
    draw_tree(d, gd, pos, 3, grow,
              green_path=("R", "L", "R") if lit else (),
              dim_rest=0.5 if lit else 0.0, node_r=6)
    # vertical tape (numbers + credential bits)
    text_c(d, 123, 58, "等和划分", F(CJKB, 22), DIMTXT)
    for i, n in enumerate(PART_NUMBERS):
        y = 96 + i * 47
        d.rounded_rectangle([64, y, 182, y + 42], radius=4, fill=PAPER,
                            outline=BRASS_D, width=2)
        text_c(d, 112, y + 8, str(n), F(SERIF, 22), INK)
        if u > b[0] + 0.5 + i * 0.35:
            d.text((152, y + 10), PART["bits"][i], font=F(SERIFB, 19),
                   fill=PURPLE)
    # formula lines, revealed per chunk
    fx = 748
    lines = [
        [("猜：", F(CJKB, 30), WHITE), (f"{ACC['guess']}", F(SERIFB, 36), ORANGE),
         (" 步", F(CJKB, 30), WHITE)],
        [("验：", F(CJKB, 30), WHITE),
         (f"{ACC['addL']} + {ACC['addR']} + 1 = {ACC['verify']}",
          F(SERIFB, 31), WHITE), (" 步", F(CJKB, 30), WHITE)],
        [("一共：", F(CJKB, 30), WHITE),
         (f"{ACC['guess']} + {ACC['verify']} = {ACC['total']}",
          F(SERIFB, 29), GOLD_L), (" 步 ≤ ", F(CJKB, 30), TEAL),
         (f"2n = {ACC['twon']}", F(SERIFB, 29), TEAL)],
        [("确定性：", F(CJKB, 30), WHITE),
         (f"{2 ** ACC['guess']} × {ACC['verify']} = ", F(SERIFB, 27), WHITE),
         (f"{ACC['det']}", F(SERIFB, 33), ORANGE), (" 步", F(CJKB, 30), WHITE)],
    ]
    for li, runs in enumerate(lines):
        if u > b[li] + 0.2:
            _runs(d, fx, 148 + li * 66, runs)
    if u > b[4] + 0.2:
        text_c(d, 640, 540, "未卜先知", F(CJK, 24), GREY)
        _runs_c(d, 640, 578,
                [(f"{ACC['total']}", F(SERIFB, 62), GOLD_L),
                 (" 对 ", F(SERIFCJKB, 40), WHITE),
                 (f"{ACC['det']}", F(SERIFB, 62), ORANGE)])
    return img

# ================= S8: equivalence, two scales =================
def shot_S8(u, ctx):
    img, glow, gd = new_frame()
    A, b, e = ctx["A"], ctx["b"], ctx["e"]
    img, d = commit(img, glow)
    fade_in(img, lambda dd: (
        text_c(dd, 640, 92, "Nondeterministic", F(SERIFB, 40), WHITE),
        text_c(dd, 640, 146, "Polynomial time", F(SERIFB, 40), WHITE)),
        seg(u, A + 0.4, A + 1.4))
    d = ImageDraw.Draw(img, "RGBA")
    tilt = 0.03 * math.sin(u * 0.8)
    draw_scale(d, gd, 300, 258, 0, 0, tilt=tilt, scale=0.62, show_vals=False)
    draw_scale(d, gd, 980, 258, 0, 0, tilt=-tilt, scale=0.62, show_vals=False)
    text_c(d, 300, 208, "猜", F(CJKB, 36), GOLD_L)
    text_c(d, 980, 208, "检查程序", F(CJKB, 36), (225, 235, 245))
    draw_conch(d, 300, 150, 24, glow_it=0.5, glow_layer=gd)
    if u > b[1]:
        text_c(d, 640, 458, "≤ p(n)", F(SERIF, 30), TEAL)
        ap = seg(u, b[1] + 0.5, b[1] + 2.5)
        y = 486
        x = 430
        while x < 430 + (850 - 430) * ap:
            d.line([x, y, min(x + 14, 850), y], fill=CYAN, width=3)
            x += 24
        if ap > 0.95:
            d.polygon([(850, y - 7), (850, y + 7), (866, y)], fill=CYAN)
        if u > b[1] + 1.0:
            text_c(d, 640, 408, "?", F(SERIFB, 36), GOLD_L)
    if u > A + ctx["a"] - 2.4:
        fa = seg(u, A + ctx["a"] - 2.4, A + ctx["a"] - 1.6)
        def fin(dd):
            _runs_c(dd, 640, 580,
                    [(PART["bits"], F(SERIF, 30), CYAN),
                     ("    ", F(SERIF, 30), WHITE),
                     (f"{PART['L']} = {PART['R']}", F(SERIFB, 30), GOLD_L)])
        fade_in(img, fin, fa)
    return img

# ================= S9: Venn platform =================
def shot_S9(u, ctx):
    img, glow, gd = new_frame()
    A, b = ctx["A"], ctx["b"]
    img, d = commit(img, glow)
    # NP platform
    d.ellipse([380, 262, 1210, 262 + 336], fill=(52, 44, 102))
    d.ellipse([380, 248, 1210, 248 + 336], fill=(96, 86, 168))
    d.ellipse([415, 268, 1175, 268 + 290], fill=(103, 93, 178))
    # P platform
    d.ellipse([343, 382, 807, 382 + 194], fill=(28, 66, 96))
    d.ellipse([343, 372, 807, 372 + 194], fill=(72, 134, 186))
    d.ellipse([368, 388, 782, 388 + 162], fill=(82, 146, 200))
    text_c(d, 795, 176, "NP", F(SERIFB, 46), PURPLE_L)
    d.text((820, 452), "P", font=F(SERIFB, 38), fill=(190, 235, 255))
    signs = [("等和划分", 560, 330, True, None), ("数独", 985, 315, True, None),
             ("扫雷", 1095, 415, True, None),
             ("分解因数", 1005, 528, True, "8616460799"),
             ("求和", 452, 468, False, None), ("找最小", 572, 442, False, None),
             ("排序", 678, 482, False, None)]
    for i, (txt, x, yb, q, sub) in enumerate(signs):
        if u > A + 0.6 + i * 0.9:
            draw_signpost(d, x, yb, txt, s=0.92, qmark=q, sub=sub)
    if u > A + 7.2:
        draw_conch(d, 462, 522, 24, glow_it=0.4, glow_layer=gd)
        draw_tape(d, 500, 508, ["1", "1", "0", "", ""], cell_w=27, cell_h=21,
                  font_size=12)
    # left panel: choice tree
    def panel(dd):
        dd.rounded_rectangle([52, 168, 330, 548], radius=12,
                             fill=(13, 14, 24, 235), outline=PURPLE, width=2)
        text_c(dd, 191, 184, "选择树", F(CJKB, 26), PURPLE_L)
        for k in range(5):
            y = 252 + k * 55
            if k < 4:
                dd.line([110, y, 110, y + 55], fill=PURPLE_L, width=2)
            dd.ellipse([105, y - 5, 115, y + 5], fill=(235, 232, 255))
        text_c(dd, 110, 512, "≤p(n)", F(SERIF, 21), TEAL)
        pos = tree_layout(215, 252, 3, 34, 60)
        draw_tree(dd, gd, pos, 3, 3.0, green_path=(), node_r=4)
    fade_in(img, panel, seg(u, A + 0.2, A + 1.2))
    d = ImageDraw.Draw(img, "RGBA")
    if u > b[1] + 0.1:
        fa = seg(u, b[1] + 0.1, b[1] + 0.9)
        fade_in(img, lambda dd: text_c(dd, 640, 594, "P ⊆ NP",
                                       F(SERIFB, 54), PURPLE_L), fa)
        img2 = img
    # slow push-in
    z = 1 + 0.045 * seg(u, 0, ctx["dur"])
    if z > 1.001:
        cw, chh = int(W / z), int(H / z)
        crop = img.crop(((W - cw) // 2, (H - chh) // 2,
                         (W - cw) // 2 + cw, (H - chh) // 2 + chh))
        img = crop.resize((W, H), Image.BICUBIC)
    return img

# ================= S10: the question + title card =================
def shot_S10(u, ctx):
    img, glow, gd = new_frame()
    A, a = ctx["A"], ctx["a"]
    img, d = commit(img, glow)
    full1 = "能快速检查答案的问题，"
    full2 = "是不是都能快速找到答案本身？"
    total = len(full1) + len(full2)
    shown = int(total * seg(u, A + 0.3, A + 10.5))
    s1 = full1[:min(shown, len(full1))]
    s2 = full2[:max(0, shown - len(full1))]
    if s1:
        text_c(d, 640, 104, s1, F(SERIFCJKB, 43), WHITE)
    if s2:
        text_c(d, 640, 164, s2, F(SERIFCJKB, 43), WHITE)
    # mini deterministic TM (left)
    draw_tape(d, 120, 440, ["1", "1", "0"], cell_w=68, cell_h=52, font_size=27)
    draw_head(img, d, 120 + 34, 440, "q0", lamp=LAMP_Q0, scale=0.85)
    text_c(d, 224, 512, "确定性图灵机", F(CJK, 22), DIMTXT)
    # dashed arrow
    ap = seg(u, ctx["b"][2], ctx["b"][2] + 2.2)
    x = 512
    while x < 512 + (800 - 512) * ap:
        d.line([x, 466, min(x + 14, 800), 466], fill=CYAN, width=3)
        x += 24
    if ap > 0.95:
        d.polygon([(800, 459), (800, 473), (816, 466)], fill=CYAN)
    # mini platform (right)
    d.ellipse([832, 402, 1178, 402 + 120], fill=(52, 44, 102))
    d.ellipse([832, 394, 1178, 394 + 120], fill=(96, 86, 168))
    d.ellipse([898, 428, 1054, 428 + 56], fill=(72, 134, 186))
    text_c(d, 1005, 340, "NP", F(SERIFB, 30), PURPLE_L)
    draw_signpost(d, 945, 452, "数独", s=0.5, qmark=True)
    draw_signpost(d, 1078, 446, "扫雷", s=0.5, qmark=True)
    text_c(d, 1005, 540, "非确定性图灵机", F(CJK, 22), DIMTXT)
    draw_conch(d, 1152, 104, 27, glow_it=0.5 + 0.3 * math.sin(u * 2),
               glow_layer=gd)
    # final title card
    if u > A + a + 0.1:
        t2 = seg(u, A + a + 0.1, A + a + 0.9)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(205 * t2)))
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
                  (0, 0))
        fade_in(img, lambda dd: text_c(dd, 640, 296, "P = NP ?",
                                       F(SERIFB, 104), WHITE), t2)
    return img

ORDER = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S7B", "S8", "S9", "S10"]
PADS = {"S1": (0.3, 0.8), "S2": (0.3, 0.8), "S3": (0.4, 1.6),
        "S4": (0.3, 0.7), "S5": (0.3, 1.0), "S6": (0.4, 1.4),
        "S7": (0.3, 1.2), "S7B": (0.3, 1.2), "S8": (0.3, 1.0),
        "S9": (0.3, 1.6), "S10": (0.3, 2.4)}
SCENES = {"S1": shot_S1, "S2": shot_S2, "S3": s3_frame, "S4": shot_S4,
         "S5": shot_S5, "S6": shot_S6, "S7": shot_S7, "S7B": shot_S7B,
         "S8": shot_S8, "S9": shot_S9, "S10": shot_S10}

PROBES = {
        "S1": [("mid", 4.5)],
        "S2": [("symbols", 3.5), ("headdrop", 7.5), ("ring", 14.6)],
        "S3": [("intro", 3.0), ("run", 16.5), ("halt", 23.5),
               ("rejflash", 24.9), ("chips", 30.5), ("thesis", 37.0)],
        "S4": [("main", 5.0)],
        "S5": [("options", 7.0), ("branches", 13.5), ("acc", 19.0),
               ("fcard", 23.5), ("strike", 22.5)],
        "S6": [("stage", 2.0), ("typein", 25.0), ("options", 22.2),
               ("running", 30.0), ("bits", 46.0), ("green", 50.0)],
        "S7": [("conch", 5.0), ("treegrow", 18.0), ("greenpath", 24.0)],
        "S7B": [("tape", 4.0), ("tree", 8.0), ("formulas", 16.0),
                ("big", 25.0)],
        "S8": [("main", 6.0), ("final", 14.2)],
        "S9": [("platform", 8.0), ("subset", 14.0)],
        "S10": [("heading", 6.0), ("arrow", 14.0), ("card", 19.8)],
    }
