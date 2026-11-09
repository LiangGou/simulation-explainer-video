# Worked example — Turing machine & NP (episode)

A complete episode built with this skill: an emulation of the Turing-machine beat (24:39–29:36) of 《这可能是人类提出最深刻的数学/计算机问题》 by 漫士沉思录 (Manshi / Lu Rui) — the segment that builds a Turing machine, runs it, breaks determinism, and lands on "P = NP ?".

**The rendered video** (`turing-segment-v1.mp4`, 4:34.5, 1280×720, 30fps, 8.65 MB) is not in this repository; it lives in the author's workspace. Everything needed to re-render it is here: `episode.py` + `timeline.json` + the narration chunks (re-synthesize with `python3 -m engine.synth` from the repo root, then `python3 -m engine.build`). Six QA stills from the original build are in `stills/`.

## Files

| File | What it is |
|---|---|
| `episode.py` | The episode contract filled in: `SEGMENTS` (locked script, TTS chunks), `SUBS` (subtitle cues), the two sims, `SCENES` (choreography), `ORDER` / `PADS` / `PROBES`, QA data (`ASR_FILES`, `EXPECTED_NUMBERS`) |
| `script-final.md` | The locked script as approved before building, including the number list with derivations |
| `shot-spec.md` | The shot-by-shot spec from frame-study of the reference, including three evidence-forced corrections to the first script draft |
| `timeline.json` | Measured narration chunk durations (output of `engine.synth`); committed so the episode renders without re-recording |
| `stills/` | Six QA stills from the original build (S3 run/halt, S5 branches, S6 green, S7 green path, S9 platform) |

## Beat-by-beat: how the episode maps onto the engine

| Segment | Beat | Simulation (episode data → archetype) | Engine pieces used |
|---|---|---|---|
| S1 | A tape draws itself on; why a machine at all | — (pure stage) | `stage.BG`, `render.new_frame/commit`, glow tape line |
| S2 | Symbols type in; the brass head drops; read / write / move; state q0 gets its ring | parity input as data | `tape_machine.draw_tape / draw_head`, `render.glyph_tile` for the write-flip |
| S3 | The parity machine runs for real; counter to 7; halts at q_acc (green); the reject state flashes as the counterfactual (what an odd count would produce); Church–Turing thesis card | `PARITY_MACHINE = TapeMachine(PARITY_DELTA, PARITY_INPUT)`; `PARITY_STEPS` drives head, tape rewrites, board highlight `(STATE_ROW[step.state], SYM_COL[step.read])`, counter `sum(counted)` | `tape_machine.draw_delta_board / draw_counter`, `title_card.statement_card` |
| S4 | Determinism: the board dims except the one live rule | same `PARITY_STEPS` | `draw_delta_board` + alpha dimming via `render.fade_in` |
| S5 | Nondeterminism: a two-rule cell; branch mini-tapes; the F-card wipe reveal; "NP = Not P" struck through | the q1-on-1 cell gains a second rule (episode data) | `tape_machine.board_cell_rect` to redraw one cell, `title_card.wipe_reveal / strikethrough` |
| S6 | The partition program: ten numbers on the tape, 0/1 option chips, balance scale with live sums, credential bits row, 254 = 254 green | `partition_sim()` on `accumulator_scale.TwoPanAccumulator(PART_CHOICE × PART_NUMBERS)`; checkpoints 103/56 → 103/194 → 254/254 all computed | `accumulator_scale.draw_scale` (values eased between sim steps), `draw_tape` with number cells |
| S7 | The magic conch over a branching tree; one green path | winning path = the partition assignment read as tree turns (episode data: `PART_CHOICE`) | `branching_tree.tree_layout / draw_tree(green_path=…)`; the conch is an episode-local prop (used once — not abstracted, per the growth discipline) |
| S7B | Accounting coda: 19 vs 9216 | `ACC` dict derived from the partition sim: guess 10 + verify (4+4+1) 9 = 19 ≤ 2n = 20; deterministic 2^10 × 9 = 9216 | `branching_tree` again + formula typesetting (episode glue) |
| S8 | Two-scales equivalence: guessing+checking ≡ certificate+checking (≤ p(n)); 254 = 254 callback | `ACC` + `PART` totals | `accumulator_scale.draw_scale` twice (two scales), `render.push_in` |
| S9 | The signature frame: purple NP platform, cyan P platform inside it, signposts, conch + mini tape inside P, choice-tree side panel, "P ⊆ NP" | membership as episode data (signpost lists) | `containment_stage.draw_platform_disc / draw_signpost / draw_side_panel`, `branching_tree` inside the panel |
| S10 | The question: deterministic machine → dashed arrow → NP platform; final card held | — | `title_card.final_card` ("P = NP ?", ~2.8 s hold) |

## What stayed in the episode (and why)

Per the growth discipline (`docs/DESIGN.md`): the magic conch prop, the "NP?" badge, the tape viewport geometry (`TAPE_Y`, `cell_cx`, `tape_cells`), the S7B formula layout, and every entrance/hold timing. None of these has recurred in a second episode yet; the conch is first in line to graduate if one does.

## Verified numbers (from the sims, asserted before choreography)

Parity run: 8 steps, 7 counted, state sequence q0→q1→q1→q0→q0→q1→q0→q0→q_acc on input `1 0 1 0 1 1 0` (four 1s, even → accept). After the halt, the choreography flashes the q_rej cell red while the narration states the counterfactual — an odd count would have stopped at reject — then the thesis card lands. Partition: total 508, final 254 = 254, credential bits `0110001101`. Accounting: 19 vs 9216, 2n = 20. All of these were re-verified through the packaged engine during this repo's smoke test.
