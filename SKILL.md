# Simulation Explainer Video — Skill

Make explainer videos the way 漫士沉思录 (Manshi) makes them: a hard topic decomposed into beats, each beat carried by a **working simulation** whose computed state drives every pixel, rendered frame-by-frame in pure Python + Pillow + ffmpeg, narrated last. This skill is platform-neutral: it runs under Muse, Claude Code, Codex, or any agent that can execute Python and shell commands. The reference implementation and a complete worked episode live in this repository.

## The method in one screen

1. **Decompose before you build.** Break the topic into beats; for each beat lock three things in the script — its topic, the transition that carries the audience in from the previous beat, and the full narration text — BEFORE any code is written. *Worked example: in the Turing episode, beat S5 (nondeterminism) opens with the exact transition line "刚才那台机器，有个规矩没改" ("that machine had one rule we haven't changed"), which exists because S4 just spent 16 seconds establishing determinism; the transition is meaningless — and unwritable — until S4's topic is locked.*
2. **Every beat gets a working simulation, not an illustration.** The visual state is computed by a small program (a machine, an accumulator, a tree, a mixture), and the renderer reads that program's state each frame. *Worked example: the parity Turing machine in S3 is a real δ table executed by `TapeMachine.run()`; when the head reads a 1 in state q1, the δ-board highlight lands on row q1 / column "1" because the step dict says `(state=q1, read=1)` — the choreography never names a cell coordinate.*
3. **Numbers are computed, never typed.** Any number that appears on screen or in the narration must be produced by the episode's sims, and the script's number list must show its derivation. *Worked example: the balance scale in S6 ends at 254 = 254 because `TwoPanAccumulator` summed the partition assignment (left set {19, 84, 78, 22, 51} = 254); the accounting coda's "19 vs 9216" is `10 guesses + 9 checks` vs `2^10 × 9`, both computed in the episode module as `ACC` — if you change one input number, every on-screen total, the narration figures, and the QA checklist update from the same source.*
4. **One stage, one palette, whole video.** A deep slate stage with a central spotlight pool; brass/beige for physical props, cyan glow for diagrams, orange only for emphasis numbers, purple only for the "suspect" class. *Worked example: across all 11 Turing segments the only purple object is the NP platform and the choice tree; the moment a second purple object appeared in drafting, the frame stopped reading as "NP = the purple thing" and the draft was corrected.*
5. **Definitions arrive late.** Demonstrate, give the everyday metaphor, run a full instance, and only then state the definition. *Worked example: NP is never defined before the audience has watched a machine guess a partition and check it in 19 steps (S6–S7B); the formal line "能在多项式时间里验证的问题" lands in S8, after the experience it names.*
6. **Thesis statements are title cards, not subtitles.** Key claims land as large centered typeset cards while the stage dims; subtitles only carry the narration. *Worked example: "P = NP ?" is a 104pt serif card held ~2.8 seconds at the end of S10 with the stage dimmed to near-black — it is also the frame a viewer screenshots.*
7. **Audio last.** Script → sims → choreography → stills QA → and only then TTS, because narration timing re-times the shots (chunk boundaries come from measured audio). *Worked example: S3's parity run starts at `A + 13.0` where A is the measured pre-pad and later beats key off chunk starts `ctx["b"][4]` — re-recording chunk 4 slower moves the thesis card automatically.*
8. **Frame 0 is the real first frame at full brightness.** No fade-in or fade-out anywhere; a platform's preview thumbnail is frame 0. *Worked example: the Turing video's frame 0 (mean luminance 37.6 vs 42.6 at t=1s, QA-checked) is the slate stage with the tape already drawing on — not a black leader.*

## The three layers

The codebase is split so an agent always knows where a change belongs:

| Layer | Where | What lives there | Rule |
|---|---|---|---|
| **Engine** | `engine/` | Mechanism only, topic-blind: frame loop, easing, glow compositing, stage + palette, subtitle burner, timeline, ffmpeg assembly, TTS/ASR adapter interfaces, QA harness | Nothing episode-specific may ever be added here |
| **Archetypes** | `engine/archetypes/` | Parameterized simulation patterns that have recurred across episodes: `tape_machine`, `weighted_mix`, `branching_tree`, `accumulator_scale`, `containment_stage`, `title_card` | Each takes data/config; none contains episode content |
| **Episode** | `examples/<topic>/`, new work from `templates/episode/` | What you generate fresh per topic: script, the episode's sim definitions (archetype instantiations with the episode's data), and shot choreography glue | Episode code may be as specific as it likes; it never edits the engine to fit |

*Worked example of the split (the Turing build, ~1,460 lines of Python): roughly 55–60% landed in engine + archetypes, ~25% is episode content-code (script data, sim definitions, subtitle cues), and ~15% is one-off choreography glue (when the conch enters, where the F-card sits). That ratio is healthy: if your episode layer is under ~15%, you are probably forcing topic content into the engine; if it is over ~50%, you are re-implementing mechanism.*

### The episode contract

An episode is a **folder** containing `episode.py` that exposes:

- `SEGMENTS` — `{segment_id: [narration chunk, ...]}`, the locked script, chunked for TTS (keep chunks ≤ ~90 CJK characters; longer calls drift slow).
- `SUBS` — `{segment_id: [subtitle cue, ...]}`, the narration split into short display phrases, in order.
- `SCENES` — `{segment_id: fn(u, ctx) -> PIL Image}`, the choreography. `u` is seconds into the segment; `ctx` carries `A` (audio start), `a` (audio duration), `dur`, `b`/`e` (chunk start/end times) from `engine.timeline.build_ctx`.
- `ORDER` — segment ids in play order. `PADS` — `{segment_id: (pre_seconds, post_seconds)}` of visual pad around the audio.
- `PROBES` — `{segment_id: [(tag, seconds), ...]}` QA still positions.
- Optional: `VOICE`, `LANG`, `OUTPUT_NAME`, `ASR_FILES`, `EXPECTED_NUMBERS` (the QA harness inputs).

The engine renders **any** folder satisfying this contract with the same commands (see Workflow). *Worked example: `examples/turing-machine-np/episode.py` is the contract filled in — its `PARITY_MACHINE = TapeMachine(PARITY_DELTA, PARITY_INPUT)` is an archetype instantiation with episode data; its magic-conch prop is defined inside the episode because it has appeared exactly once (see Growth discipline).*

### Growth discipline — when code may move layers

**Abstract only what has recurred in two episodes. A shape needed once stays in the episode layer. On its third appearance, it graduates to the archetypes.** Never generalize speculatively: a pattern abstracted from a single instance encodes that instance's accidents as if they were the pattern's essence.

*Worked example: `weighted_mix` exists because arcs-with-weights appeared in the attention PoC (attention weights over tokens) and were needed again in general form; `branching_tree` graduated because the Turing episode alone used the same tree three times (S7 growth, S7B accounting, S9 panel) after the pattern had already appeared as the PoC's multi-head fan-out. The magic conch, by contrast, has appeared once — it stays in `examples/turing-machine-np/episode.py`, and if a future episode needs a "mascot prop" a second time, only then does a `prop` archetype get designed, from two real instances.*

## Production workflow (step by step)

1. **Research / frame-study (only when imitating a reference).** Watch the reference; if frames matter, obtain the video file and extract frames locally with ffmpeg; write a shot-spec that maps every shot to its on-screen elements and sim behavior. Correct the script draft against frame evidence, not memory. *Worked example: the Turing shot-spec (`examples/turing-machine-np/shot-spec.md`) records three evidence-forced corrections — the reference's S3 machine is a PARITY machine (blackboard title "1 的个数是偶数？"), not the erase machine the first script draft assumed; the partition segment puts the numbers ON the tape with a live-sum scale; the conch is a literal prop inside the P platform.*
2. **Script.** Copy `templates/script-template.md`; fill the beat table (topic / transition-in / narration / simulation / visual / duration) for every beat; write full narration text; end with a number list giving every spoken or shown number and its derivation from the sims. Get the script approved/locked before building. *Worked example: the Turing script's number list reads "508 = sum of the ten numbers; 254 = half; 1024 = 2^10; 9216 = 1024 × 9; 19 = 10 + 9; 7 = cells processed by the parity machine" — every entry traceable to one line of the episode's sim code.*
3. **Sims.** Write the episode's simulations first, as data on archetypes where one fits (`TapeMachine(delta, input)`, `TwoPanAccumulator(choices)`, `WeightedMix(weights)`), else as plain functions in the episode module. Run them standalone and assert the headline numbers before any drawing code exists. *Worked example: `PARITY_STEPS` has 8 steps, 7 counted, state sequence q0→q1→q1→q0→q0→q1→q0→q0→q_acc — asserted in one line of Python before S3 was choreographed.*
4. **Choreography.** One scene function per segment; each frame: `new_frame()` → draw glow elements → `commit()` → draw props/text from sim state → return image. Time everything off `ctx` (chunk boundaries), never absolute guesses.
5. **QA stills.** `python3 -m engine.build <episode_dir> stills` renders `PROBES` frames. READ every still yourself; fix composition defects (clipping, overlaps, labels escaping panels) before rendering. *Worked example: the Turing build's stills pass caught 7+ defects, including the δ-board right column clipping and the S9 panel tree escaping its frame — all invisible in code, all obvious in one still.*
6. **Audio.** `python3 -m engine.synth <episode_dir>` synthesizes chunks via the TTS adapter (see `docs/adapters.md`), measures durations, writes `timeline.json`. Then check narration pace per segment (characters/sec); split any segment that runs slow and re-synthesize.
7. **ASR verification.** `python3 -m engine.qa asr <episode_dir>` — faster-whisper small AND medium transcribe the number-bearing segments; every token in `EXPECTED_NUMBERS` must be heard by both. A miss means re-record that chunk (reword or slow down), never ship and hope. *Worked example: in a sibling production, ASR heard "200型" for "前两百行" — the fix was rewording the line to "上限是前两百行、二十五 KB", after which both models transcribed it exactly.*
8. **Full render + final checks.** `python3 -m engine.build <episode_dir>`; then `python3 -m engine.qa frame0 <episode_dir>/<OUTPUT_NAME>`; spot-read stills at segment boundaries from the rendered video; verify total duration and that frame 0 is shot 1 at full brightness. Deliver the mp4 path, duration, and the QA results — including any fidelity gaps you know about, named as gaps.

## Engine API (quick reference)

- `engine.stage` — `W, H, FPS`; palette constants; `F(path, size)` cached fonts (`CJK, CJKB, SERIF, SERIFB, SANS, SANSB, SERIFCJK…`, overridable via `SEV_FONT_*` env vars); `seg(t, t0, t1)` progress, `ease_out`, `ease_io`, `lerp`, `mix`, `clamp`; `text_c(d, cx, y, s, font, fill)`; `BG` the stage backdrop.
- `engine.render` — `new_frame()` → `(img, glow, glow_draw)`; `commit(img, glow)` → `(img, sharp_draw)`; `glyph_tile(sym, font, color)` for symbol flips; `fade_in(base, draw_fn, a)`; `push_in(img, z)` the camera move; `render_episode_frame(episode, seg_id, u, ctx)` scene + subtitle.
- `engine.timeline.build_ctx(tl_entry, pre, post)` → `{A, a, dur, b, e}`.
- `engine.subs` — `draw_subtitle(d, text)`; `subtitle_at(cues, u, A, a)` (length-weighted cue scheduling).
- `engine.adapters` — `tts_synthesize(text, out, voice, lang)`, `ffprobe_duration(path)`, `asr_transcribe(path, size)`, `check_numbers(path, expected)`. Configuration: `SEV_TTS_CMD` template or `SEV_TTS_BIN`; see `docs/adapters.md`.
- Archetypes (`from engine.archetypes import …` or per-module):
  - `tape_machine.TapeMachine(delta, input, start_state, blank, halt_states).run()` → step dicts `{state, pos, read, write, next, tape_before, counted}`; `.board_rows(states, symbols)` → `(rows, row_of, col_of)`; drawing: `draw_tape`, `draw_head` (lamp colors `LAMP_Q0/Q1/ACC/REJ`), `draw_counter`, `draw_delta_board(..., highlight=(row, col))`, `board_cell_rect`.
  - `weighted_mix.WeightedMix(weights).shares()`, `.blend(colors, base)`; `draw_mix_arcs(d, glow, src_xy, targets, mix, progress, flow_phase)`; `draw_share_label`. *Use for attention, mixtures, weighted votes.*
  - `branching_tree.tree_layout(cx, y0, depth, dx0, dy)`, `draw_tree(d, glow, pos, depth, grow_levels, green_path)`. *The green path is data — feed it the path your sim actually took.*
  - `accumulator_scale.TwoPanAccumulator([(side, value), …]).steps()` → per-step `{L, R}` totals; `draw_scale(d, glow, cx, top_y, L, R, tilt, green, pan_cards)`.
  - `containment_stage.draw_platform_disc`, `draw_signpost(..., qmark, sub)`, `draw_side_panel` → inner rect.
  - `title_card.wipe_reveal(img, lines, progress)`, `statement_card(d, rect, title, body)`, `final_card(img, text, progress)`, `strikethrough(d, x0, x1, y, progress)`.

### How to add a new sim (episode layer)

Define it as data + a run function in the episode module, returning step dicts; assert its headline outputs in a scratch check before choreographing. *Worked example: to add a sorting beat, write `SORT_STEPS = bubble_sort_steps([5, 2, 9, 1])` returning per-swap array states, assert the final state is sorted and the swap count matches the narration's claim, then draw bars whose heights are `SORT_STEPS[k]` — the bars can never show an unsorted "final" by accident.*

### How to add a shot

Add `SEGMENTS[seg_id]`, `SUBS[seg_id]`, a `shot_fn(u, ctx)`, register it in `SCENES`, `ORDER`, `PADS`, `PROBES`; re-run synth (timing), stills (composition), then build. *Worked example: S7B (the accounting coda) was added after S1–S10 existed — one new scene function reusing `branching_tree` and the episode's `ACC` dict, two new probes (`tree`, `formulas`), no engine changes.*

## Done-criteria checklist (per video)

- [ ] Script locked before building: every beat has topic, transition-in, full narration; the number list derives every number from the sims.
- [ ] Every on-screen number, highlight, counter, and total traces to a sim run (grep the choreography for numeric literals that should be sim outputs — there should be none).
- [ ] Sims asserted standalone (final states, totals, counts match the script's claims exactly).
- [ ] QA stills rendered for every segment and READ; composition defects fixed and re-stilled.
- [ ] Narration pace checked per segment; slow segments split and re-synthesized.
- [ ] Dual-ASR number check passes on both models for every token in `EXPECTED_NUMBERS`.
- [ ] Frame-0 check passes (no fade, frame 0 = first shot at full brightness).
- [ ] Boundary stills from the FINAL mp4 spot-read (not just from the stills pass).
- [ ] Fidelity gaps declared in the delivery note (what is schematic vs exact), never smoothed over.

*Worked example: the Turing delivery met every line — dual-ASR exact on 1024 / 9216 / 19 / 254 / 508 / 7步； frame-0 luminance 37.6 vs 42.6 at 1s; and its delivery note still declared the gaps: 2.5D PIL props vs the reference's true 3D, a schematic two-row δ board in one shot, and a ~1.5s lamp/board sequencing nit in S3.*
