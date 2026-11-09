"""Archetypes: simulation patterns that recurred across two real
episodes (the attention PoC and the Turing build) and were abstracted
only after recurring. Each takes data/config; none contains episode
content. See SKILL.md for the growth discipline that governs what may
be added here.
"""
from engine.archetypes.tape_machine import (  # noqa: F401
    TapeMachine, draw_tape, draw_head, draw_counter,
    draw_delta_board, board_cell_rect)
from engine.archetypes.weighted_mix import (  # noqa: F401
    WeightedMix, draw_mix_arcs, draw_share_label, arc_points, arc_height)
from engine.archetypes.branching_tree import (  # noqa: F401
    tree_layout, draw_tree)
from engine.archetypes.accumulator_scale import (  # noqa: F401
    TwoPanAccumulator, draw_scale)
from engine.archetypes.containment_stage import (  # noqa: F401
    draw_platform_disc, draw_signpost, draw_side_panel)
from engine.archetypes.title_card import (  # noqa: F401
    wipe_reveal, statement_card, final_card, strikethrough)
