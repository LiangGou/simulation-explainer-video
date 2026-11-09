#!/usr/bin/env python3
"""ENGINE LAYER — burned-in subtitles.

One cue at a time, white bold sans, bottom center, thin dark outline,
no background box (the reference style). The cue list itself is episode
data (episode.SUBS); this module only schedules and draws.

Scheduling: cues are weighted by character count and spread across the
segment's narration window, so a long sentence stays on screen longer
than a short one without anyone hand-timing 90+ cues.
"""
from engine.stage import F, CJKB, WHITE, W


def draw_subtitle(d, text, cx=None, y=662):
    if not text:
        return
    if cx is None:
        cx = W // 2
    f = F(CJKB, 30)
    d.text((cx, y), text, font=f, fill=WHITE, anchor="ma",
           stroke_width=3, stroke_fill=(8, 9, 12))


def subtitle_at(cues, u, audio_start, audio_dur):
    """Return the cue visible at local time u, or None outside the
    narration window [audio_start, audio_start + audio_dur]."""
    if u < audio_start or u > audio_start + audio_dur:
        return None
    weights = [max(4, len(c)) for c in cues]
    tot = sum(weights)
    x = (u - audio_start) / audio_dur * tot
    acc = 0.0
    for c, w in zip(cues, weights):
        acc += w
        if x <= acc:
            return c
    return cues[-1]
