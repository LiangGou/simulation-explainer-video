# Adapters — the two environment plugs

The engine is platform-neutral. Exactly two capabilities depend on the machine it runs on, and both sit behind small interfaces in `engine/adapters.py`. An agent on a different platform swaps these without touching the engine, the archetypes, or any episode.

## TTS adapter (narration out)

**Interface:** `tts_synthesize(text, out_path, voice=None, lang="zh") -> out_path` — turn one chunk of narration text into an mp3 file at `out_path`. Chunks are short (≤ ~90 CJK characters in the reference workflow) because long synthesis calls drift slow and re-recording one line should not re-bill the whole narration.

**Resolution order** (first match wins):

1. `SEV_TTS_CMD` environment variable — a command template with `{text}`, `{out}`, `{voice}`, `{lang}` placeholders. This is the universal plug: any CLI TTS (edge-tts, a cloud CLI, a local model wrapper) fits.
2. `SEV_TTS_BIN` — a binary with the Muse flag convention: `<bin> --text T --voice V --language L --output OUT`.
3. `/opt/hatch/bin/tts` if present (the Muse default).

**Worked example (Muse implementation):** the Turing episode pins `VOICE = "avocado_v2:MAI_01"` (the Aria voice, chosen by the author for all narration) and `LANG = "zh"`. On the Muse VM, `engine.synth` calls `/opt/hatch/bin/tts --text <chunk> --voice avocado_v2:MAI_01 --language zh --output audio/chunks/s3-0.mp3` per chunk, measures each result with ffprobe, and writes `timeline.json`. The same episode on another platform needs only e.g. `SEV_TTS_CMD='edge-tts --voice zh-CN-XiaoxiaoNeural --text "{text}" --write-media "{out}"'` — no code changes.

**Contract notes:** the synthesizer must produce a real mp3 (> 1 KB) at `out_path` or raise; silent failure is the one unforgivable mode, because downstream stages would time shots against a missing narration. Voice choice is episode data (`VOICE`), never engine data — a different narrator is a different episode decision.

## ASR adapter (verification in)

**Interface:** `asr_transcribe(audio_path, model_size) -> text` and `check_numbers(audio_path, expected) -> {model: {token: bool}}`, where `expected` maps each number token to its accepted transcript spellings (digits or written-out forms).

**Reference implementation:** faster-whisper (`pip install faster-whisper`, the only optional dependency), CPU int8, `language="zh"`, beam 5. The QA harness always runs **two model sizes** (`small` and `medium`): a number both models hear identically is a number the audience will hear correctly; a number only the larger model catches is a mispronunciation risk in the wild.

**Worked example:** the Turing episode declares `EXPECTED_NUMBERS = {"1024": ["1024", "一千零二十四"], "9216": [...], "254": ["254", "二百五十四"], "7steps": ["七步", "7步"], ...}` and `ASR_FILES = ["s3", "s6", "s7b"]`. `python3 -m engine.qa asr examples/turing-machine-np` transcribes those segments with both models and fails the build on any missed token. The established fix for a miss is at the script layer, not the audio layer: reword the line (a sibling production changed "前两百行" to "上限是前两百行、二十五 KB" after ASR misheard it) or split the chunk, then re-synthesize just that chunk and re-check.

**Swapping:** any ASR behind the same two functions works — whisper.cpp, a cloud STT CLI, or an OS dictation service. Keep the two-model rule by configuring two model sizes or two independent engines; the point is independent agreement, not the brand.
