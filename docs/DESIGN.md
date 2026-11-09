# Design — the three-layer architecture

This project is organized in three layers so that an agent working on any episode always knows where a change belongs, and so the reusable core never absorbs topic-specific accidents.

## Layer 1 — Engine (`engine/`)

Mechanism only. Topic-blind. It knows how to: hold a stage (canvas, palette, fonts, spotlight backdrop), run a frame loop with a glow pass and a sharp pass, ease and interpolate, schedule and burn subtitles, turn measured audio chunks into segment timing, assemble segments with ffmpeg, talk to the outside world through two adapter plugs (TTS out, ASR in), and run the QA harness (ASR number check, boundary stills, frame-0 check).

The engine contains no episode nouns: no Turing machines, no partitions, no numbers from any script. If a proposed engine change names a topic, it belongs in a lower layer.

## Layer 2 — Archetypes (`engine/archetypes/`)

Parameterized simulation patterns — the shapes that recur across explainer topics:

| Archetype | Pattern | Recurrence evidence |
|---|---|---|
| `tape_machine` | a tape, a moving head, a rule table whose highlight follows the machine's state | Turing build (parity machine, partition machine); the generic δ/alphabet form was needed twice inside one episode |
| `weighted_mix` | one source, weighted arcs to many targets, shares as percentages, value color flowing back, source color blending | attention PoC (token attention) — abstracted when the pattern was specified a second time for mixture-style beats |
| `branching_tree` | a choice tree growing level by level, one root-to-leaf path lit as the winner | Turing build used it three times (growth, accounting, panel gloss) |
| `accumulator_scale` | two running totals on a balance; tilt from the difference, green at equality | Turing build (partition sums); the two-running-totals shape is the standard "compare as you go" beat |
| `containment_stage` | a set as a platform, a subset as a platform on it, members as signposts, a side panel for a gloss diagram | Turing build (P inside NP); set-inclusion beats recur in any classification topic |
| `title_card` | thesis statements as physical cards: wipe reveal, statement card, final hold card, strikethrough correction | both episodes (attention PoC title card; Turing thesis card, F-card, final "P = NP ?") |

An archetype takes data and configuration (a δ table, a weight dict, a list of choices, a path tuple) and never contains episode content: the parity δ and the partition numbers live in the example episode, not in `tape_machine.py`.

## Layer 3 — Episode (`examples/<topic>/`, starters in `templates/episode/`)

What an agent generates fresh for each topic:

- **script** — `SEGMENTS` (narration chunks) and `SUBS` (subtitle cues) in `episode.py`, authored from `templates/script-template.md`, plus a shot-spec from `templates/shot-spec-template.md`;
- **sim definitions** — archetype instantiations with the episode's data (e.g. `TapeMachine(PARITY_DELTA, PARITY_INPUT)`), or plain episode-local sim functions when no archetype fits yet;
- **choreography glue** — the scene functions: entrances, holds, label placements, camera pushes, which sim step drives which second. This glue is expected to be one-off and is NOT a defect.

The engine renders any episode folder through the same entry points (`engine.synth`, `engine.build`, `engine.qa`), driven entirely by the episode contract in SKILL.md.

## The growth discipline

**Abstract only what has recurred in two episodes. A shape needed once stays in the episode layer. On its third appearance, it graduates to the archetypes.**

Rationale: an abstraction designed from one instance encodes that instance's accidents as essence (the parity machine's exact board geometry is not "the tape machine pattern"; the pattern is *state drives highlight*). Two instances are the minimum evidence that a shape is a pattern; the third use is where the abstraction pays for itself.

The Turing build's own split is the calibration example: of its ~1,460 lines of Python, roughly 55–60% generalized into engine + archetypes, ~25% is episode content-code (script data, sim definitions, subtitle cues), and ~15% is one-off choreography that correctly stayed in the episode. The magic conch is the discipline's mascot: a beloved prop, used exactly once, deliberately NOT abstracted — it sits in the example's `episode.py`, and a `prop` archetype will be designed only when a second episode needs a mascot, from two real instances.

## Dependency direction

Episode → archetypes → engine. Never the reverse: the engine does not import episodes, and archetypes do not import each other (compose them in the episode instead). Adapters are the only place environment specifics (a TTS binary path, a whisper install) may appear, and they sit behind the interfaces in `engine/adapters.py` — see `docs/adapters.md`.
