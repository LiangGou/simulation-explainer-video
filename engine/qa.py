#!/usr/bin/env python3
"""ENGINE LAYER — QA harness. Three checks, all mandatory before delivery.

  asr     python3 -m engine.qa asr <episode_dir>
          Transcribe the episode's ASR_FILES segments with faster-whisper
          small AND medium; every token in episode.EXPECTED_NUMBERS must
          be heard identically by both models. A number only one model
          hears correctly is a number part of the audience will mishear
          — re-record that chunk (slower, or reworded) and re-check.
          Worked example (Turing episode): the token 254=254 appears in
          the narration as 二百五十四 and on the scale as digits; both
          models must produce it in segments s6 and s7b.

  frame0  python3 -m engine.qa frame0 <video.mp4>
          Frame 0 must be the real first shot at full brightness — the
          reference workflow has NO fade-in anywhere (a platform's
          preview thumbnail is frame 0). Compares mean luminance of
          frame 0 vs frame at 1.0s; frame 0 must not be near-black and
          must be within 40% of the 1.0s frame.

  stills  handled by engine.build stills mode; the check is a human /
          agent READING every still — see SKILL.md done-criteria.
"""
import os
import subprocess
import sys

from PIL import Image

from engine.adapters import check_numbers
from engine.loader import load_episode


def mean_luminance(img):
    g = img.convert("L").resize((64, 36))
    px = list(g.getdata())
    return sum(px) / len(px)


def frame0_check(video_path):
    tmp = "/tmp/sev-frame0"
    os.makedirs(tmp, exist_ok=True)
    frames = []
    for name, ss in (("f0.png", "0"), ("f1.png", "1.0")):
        p = os.path.join(tmp, name)
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", ss, "-i",
                            video_path, "-frames:v", "1", p, "-y"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("frame0: ffmpeg failed", r.stderr[-300:])
            return False
        frames.append(mean_luminance(Image.open(p)))
    l0, l1 = frames
    ok = l0 > 12 and l0 >= 0.6 * l1
    print(f"frame0: mean luminance frame0={l0:.1f} frame@1s={l1:.1f} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def asr_check(episode_dir):
    ep = load_episode(episode_dir)
    expected = getattr(ep, "EXPECTED_NUMBERS", None)
    files = getattr(ep, "ASR_FILES", None)
    if not expected or not files:
        print("asr: episode defines no EXPECTED_NUMBERS / ASR_FILES — SKIP")
        return True
    ok = True
    for name in files:
        path = os.path.join(episode_dir, "audio", f"{name}.mp3")
        res = check_numbers(path, expected)
        for model, toks in res.items():
            bad = [t for t, v in toks.items() if not v]
            print(f"asr: {name} [{model}] "
                  + ("PASS all tokens" if not bad else f"MISS {bad}"))
            ok = ok and not bad
    return ok


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "asr":
        sys.exit(0 if asr_check(sys.argv[2]) else 1)
    if len(sys.argv) >= 3 and sys.argv[1] == "frame0":
        sys.exit(0 if frame0_check(sys.argv[2]) else 1)
    print(__doc__)
    sys.exit(2)
