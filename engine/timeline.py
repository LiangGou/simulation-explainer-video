#!/usr/bin/env python3
"""ENGINE LAYER — segment timing.

An episode's narration is synthesized in chunks (see engine/synth.py).
timeline.json records each chunk's measured audio duration. A scene's
choreography never hard-codes seconds: it reads chunk boundaries from
the context built here, so re-recording a line with a slower voice
re-times the whole shot automatically.

Context fields:
  A    seconds of silence before the narration starts (pre-pad)
  a    total narration duration of the segment
  dur  total segment duration (pre-pad + narration + post-pad)
  b    list of chunk start times (b[i] = when chunk i begins)
  e    list of chunk end times

Worked example (Turing episode, segment S3): PADS gives (0.4, 1.6);
the parity machine starts its run at A + 13.0 inside the choreography,
which lands inside chunk 3 because b[3] is derived from the measured
chunk durations — not from a stopwatch.
"""


def build_ctx(tl_entry, pre, post):
    """tl_entry: {"chunks": [{"dur": float, ...}], "audio_dur": float}
    pre, post: the episode's PADS entry for this segment."""
    a = tl_entry["audio_dur"]
    bounds, ends = [], []
    t = pre
    for c in tl_entry["chunks"]:
        bounds.append(round(t, 3))
        t += c["dur"]
        ends.append(round(t, 3))
    return {"A": pre, "a": a, "dur": pre + a + post, "b": bounds, "e": ends}
