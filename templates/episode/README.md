# Starting a new episode

1. Copy this folder to `examples/<your-topic>/` (or anywhere — the engine renders any folder with an `episode.py`).
2. Write the script first, in `templates/script-template.md` form: beat table locked (topic / transition / narration / simulation) before any code. Write the shot-spec from `templates/shot-spec-template.md`.
3. Fill `episode.py`: `SEGMENTS` and `SUBS` from the locked script; sims as archetype instantiations with your data; one scene function per segment reading sim state.
4. Run the pipeline from the repo root:

```bash
python3 -m engine.synth examples/<your-topic>          # narration -> timeline.json
python3 -m engine.build examples/<your-topic> stills   # QA stills — read every one
python3 -m engine.qa asr examples/<your-topic>         # dual-ASR number check
python3 -m engine.build examples/<your-topic>          # full render
python3 -m engine.qa frame0 examples/<your-topic>/final.mp4
```

5. Check the delivery against the done-criteria in `SKILL.md`. If a visual shape turns out to be needed by a second episode, note it — on its third appearance it graduates to `engine/archetypes/` (see `docs/DESIGN.md`, growth discipline).
