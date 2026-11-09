#!/usr/bin/env python3
"""EPISODE LAYER — <episode-id> (starter skeleton).

Copy this folder, rename it to your topic, and fill in:
  1. SEGMENTS  — the locked script, chunked for TTS (from your
                 templates/script-template.md beat table).
  2. SUBS      — subtitle cues: the narration split into short
                 phrases, in order, per segment.
  3. Sims      — archetype instantiations with YOUR data (a delta
                 table, a weight dict, a choice list), or plain
                 episode-local sim functions. Assert their outputs
                 before choreographing.
  4. SCENES    — one choreography function per segment. Each frame:
                 new_frame() -> glow pass -> commit() -> sharp pass
                 drawn from sim state -> return img.
  5. PROBES    — QA still positions per segment.

Then: python3 -m engine.synth <this folder>
      python3 -m engine.build <this folder> stills   (READ them)
      python3 -m engine.qa asr <this folder>
      python3 -m engine.build <this folder>
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageChops

from engine.stage import *
from engine.render import new_frame, commit, glyph_tile, fade_in
# Import the archetypes your sims use, e.g.:
# from engine.archetypes.tape_machine import TapeMachine, draw_tape, \
#     draw_head, draw_counter, draw_delta_board, board_cell_rect
# from engine.archetypes.weighted_mix import WeightedMix, draw_mix_arcs
# from engine.archetypes.branching_tree import tree_layout, draw_tree
# from engine.archetypes.accumulator_scale import TwoPanAccumulator, draw_scale
# from engine.archetypes.containment_stage import draw_platform_disc, draw_signpost
from engine.archetypes.title_card import final_card

EPISODE_ID = "my-episode"
VOICE = "avocado_v2:MAI_01"
LANG = "zh"
OUTPUT_NAME = "final.mp4"

# QA harness inputs (optional but expected for any number-bearing beat)
ASR_FILES = []
EXPECTED_NUMBERS = {}

# ------------------------------------------------------------ script
SEGMENTS = {
    "S1": ["<narration chunk 1>", "<narration chunk 2>"],
}
SUBS = {
    "S1": ["<cue 1>", "<cue 2>"],
}

# ------------------------------------------------------------ sims
# MY_SIM_STEPS = MySim(...).run()   # assert the headline outputs here


# ------------------------------------------------------------ scenes
def shot_S1(u, ctx):
    img, glow, gd = new_frame()
    img, d = commit(img, glow)
    # draw your beat from sim state here; the stub holds a title card
    img = final_card(img, "<THESIS LINE>", seg(u, 1.0, 2.0))
    return img


SCENES = {"S1": shot_S1}
ORDER = ["S1"]
PADS = {"S1": (0.4, 1.2)}
PROBES = {"S1": [("card", 3.0)]}
