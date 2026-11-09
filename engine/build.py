#!/usr/bin/env python3
"""ENGINE LAYER — build driver. Renders ANY episode folder the same way.

Usage:
  python3 -m engine.build <episode_dir> stills   # QA stills only
  python3 -m engine.build <episode_dir>          # full render

stills mode renders the frames listed in episode.PROBES
({segment_id: [(tag, seconds), ...]}) into <episode_dir>/stills/ —
always run it and READ every still before paying for a full render.

Full render: per segment, draw FPS frames at the segment's computed
duration, encode with ffmpeg, delay+pad the segment audio to match,
concatenate all segments, mux. Output: <episode_dir>/<OUTPUT_NAME>
(episode.OUTPUT_NAME, default "final.mp4").
"""
import os
import shutil
import subprocess
import sys

from engine.loader import load_episode, load_timeline
from engine.render import render_episode_frame
from engine.stage import FPS
from engine.timeline import build_ctx


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd[:6]), r.stderr[-500:])
        sys.exit(1)


def _ctxs(ep, tl):
    return {seg: build_ctx(tl[seg], *ep.PADS[seg]) for seg in ep.ORDER}


def stills(episode_dir):
    ep = load_episode(episode_dir)
    tl = load_timeline(episode_dir)
    ctxs = _ctxs(ep, tl)
    out = os.path.join(episode_dir, "stills")
    os.makedirs(out, exist_ok=True)
    for seg_id in ep.ORDER:
        ctx = ctxs[seg_id]
        for tag, u in getattr(ep, "PROBES", {}).get(seg_id, []):
            if u > ctx["dur"]:
                print("skip", seg_id, tag, u, ">", round(ctx["dur"], 1))
                continue
            img = render_episode_frame(ep, seg_id, u, ctx)
            p = os.path.join(out, f"{seg_id.lower()}-{tag}.png")
            img.save(p)
            print("still", p)


def render_all(episode_dir):
    ep = load_episode(episode_dir)
    tl = load_timeline(episode_dir)
    ctxs = _ctxs(ep, tl)
    segs_dir = os.path.join(episode_dir, "segs")
    os.makedirs(segs_dir, exist_ok=True)
    frames_dir = os.path.join(episode_dir, "frtmp")
    seg_videos, seg_audios = [], []
    total = 0.0
    for seg_id in ep.ORDER:
        ctx = ctxs[seg_id]
        dur = ctx["dur"]
        total += dur
        n = int(dur * FPS)
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
        os.makedirs(frames_dir)
        for i in range(n):
            img = render_episode_frame(ep, seg_id, i / FPS, ctx)
            img.save(os.path.join(frames_dir, f"f{i:05d}.png"))
        vout = os.path.join(segs_dir, f"{seg_id.lower()}.mp4")
        run(["ffmpeg", "-y", "-framerate", str(FPS), "-i",
             os.path.join(frames_dir, "f%05d.png"), "-c:v", "libx264",
             "-crf", "17", "-pix_fmt", "yuv420p", vout])
        shutil.rmtree(frames_dir)
        aout = os.path.join(segs_dir, f"{seg_id.lower()}.wav")
        pre_ms = int(ctx["A"] * 1000)
        run(["ffmpeg", "-y", "-i",
             os.path.join(episode_dir, "audio", f"{seg_id.lower()}.mp3"),
             "-af", f"adelay={pre_ms}:all=1,apad", "-t", f"{dur:.3f}", aout])
        seg_videos.append(vout)
        seg_audios.append(aout)
        print(f"segment {seg_id}: video {dur:.1f}s done", flush=True)
    vlist = os.path.join(segs_dir, "vlist.txt")
    with open(vlist, "w") as f:
        for v in seg_videos:
            f.write(f"file '{v}'\n")
    silent = os.path.join(episode_dir, "video-silent.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", vlist,
         "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", silent])
    alist = os.path.join(segs_dir, "alist.txt")
    with open(alist, "w") as f:
        for a in seg_audios:
            f.write(f"file '{a}'\n")
    full_audio = os.path.join(episode_dir, "audio-full.wav")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", alist,
         "-c:a", "pcm_s16le", full_audio])
    final = os.path.join(episode_dir,
                          getattr(ep, "OUTPUT_NAME", "final.mp4"))
    run(["ffmpeg", "-y", "-i", silent, "-i", full_audio, "-c:v", "copy",
         "-c:a", "aac", "-b:a", "160k", "-shortest", final])
    print("TOTAL visual duration:", round(total, 1), "s")
    print("FINAL:", final)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    if len(sys.argv) > 2 and sys.argv[2] == "stills":
        stills(sys.argv[1])
    else:
        render_all(sys.argv[1])
