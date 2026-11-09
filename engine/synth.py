#!/usr/bin/env python3
"""ENGINE LAYER — narration synthesis driver.

Usage:  python3 -m engine.synth <episode_dir>

Reads episode.SEGMENTS ({segment_id: [chunk_text, ...]}), synthesizes
each chunk through the TTS adapter, concatenates chunks into
audio/<segment>.mp3, measures every duration with ffprobe, and writes
timeline.json — the single source of timing truth for rendering and
subtitle scheduling.

Audio is synthesized LAST in the workflow (after script, sims, and
shot choreography are locked) and re-synthesized whenever the script
changes. Existing chunk mp3s larger than 1 KB are reused, so fixing
one line does not re-bill the whole narration.
"""
import json
import os
import subprocess
import sys

from engine.adapters import ffprobe_duration, tts_synthesize
from engine.loader import load_episode


def synthesize(episode_dir):
    ep = load_episode(episode_dir)
    voice = getattr(ep, "VOICE", None)
    lang = getattr(ep, "LANG", "zh")
    chunks_dir = os.path.join(episode_dir, "audio", "chunks")
    os.makedirs(chunks_dir, exist_ok=True)
    timeline = {}
    for seg_id, chunks in ep.SEGMENTS.items():
        entries = []
        for i, text in enumerate(chunks):
            out = os.path.join(chunks_dir, f"{seg_id.lower()}-{i}.mp3")
            if not (os.path.exists(out) and os.path.getsize(out) > 1000):
                tts_synthesize(text, out, voice=voice, lang=lang)
            entries.append({
                "file": f"audio/chunks/{seg_id.lower()}-{i}.mp3",
                "text": text,
                "dur": round(ffprobe_duration(out), 3),
            })
            print(seg_id, i, entries[-1]["dur"], text[:20], flush=True)
        segmp3 = os.path.join(episode_dir, "audio", f"{seg_id.lower()}.mp3")
        lst = os.path.join(chunks_dir, f"{seg_id.lower()}.txt")
        with open(lst, "w") as f:
            for e in entries:
                f.write(f"file '{os.path.join(chunks_dir, os.path.basename(e['file']))}'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c", "copy", segmp3, "-y"], check=True)
        timeline[seg_id] = {
            "chunks": entries,
            "audio_dur": round(sum(e["dur"] for e in entries), 3),
        }
    with open(os.path.join(episode_dir, "timeline.json"), "w") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=1)
    total = sum(v["audio_dur"] for v in timeline.values())
    print("TOTAL AUDIO", round(total, 1), "s -> timeline.json")
    return timeline


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    synthesize(sys.argv[1])
