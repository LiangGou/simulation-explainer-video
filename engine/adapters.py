#!/usr/bin/env python3
"""ENGINE LAYER — environment adapters (TTS out, ASR check in).

The engine itself never calls a vendor API. Two plugs connect it to
whatever machine it runs on:

  TTS  synthesize(text, out_path) -> mp3 file
  ASR  transcribe(audio_path, model_size) -> text, for number checks

The worked implementation below targets the Muse environment
(/opt/hatch/bin/tts). On any other platform, set SEV_TTS_CMD to a
command template and nothing else changes — see docs/adapters.md.

TTS command resolution order:
  1. explicit cmd_template argument
  2. $SEV_TTS_CMD   (placeholders: {text} {out} {voice} {lang})
  3. $SEV_TTS_BIN, or /opt/hatch/bin/tts if present, called as
     <bin> --text T --voice V --language L --output OUT
  4. RuntimeError with setup instructions
"""
import os
import shlex
import subprocess

DEFAULT_VOICE = os.environ.get("SEV_TTS_VOICE", "avocado_v2:MAI_01")
MUSE_TTS = "/opt/hatch/bin/tts"


class AdapterError(RuntimeError):
    pass


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise AdapterError(
            f"command failed: {cmd[0]} ...\n{r.stdout[-300:]}\n{r.stderr[-300:]}")
    return r


def tts_synthesize(text, out_path, voice=None, lang="zh", cmd_template=None):
    """Synthesize one narration chunk to an mp3 at out_path."""
    voice = voice or DEFAULT_VOICE
    tmpl = cmd_template or os.environ.get("SEV_TTS_CMD")
    if tmpl:
        cmd = shlex.split(tmpl.format(text=text, out=out_path,
                                      voice=voice, lang=lang))
        _run(cmd)
    else:
        binp = os.environ.get("SEV_TTS_BIN") or (
            MUSE_TTS if os.path.exists(MUSE_TTS) else None)
        if not binp:
            raise AdapterError(
                "No TTS configured. Set SEV_TTS_CMD to a command template "
                "with {text} {out} {voice} {lang} placeholders, or "
                "SEV_TTS_BIN to a Muse-style tts binary. "
                "See docs/adapters.md.")
        _run([binp, "--text", text, "--voice", voice,
              "--language", lang, "--output", out_path])
    if not (os.path.exists(out_path) and os.path.getsize(out_path) > 1000):
        raise AdapterError(f"TTS produced no usable file at {out_path}")
    return out_path


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv", path], capture_output=True, text=True)
    if out.returncode != 0:
        raise AdapterError(f"ffprobe failed on {path}")
    return float(out.stdout.strip().split(",")[1])


def asr_transcribe(audio_path, model_size="small"):
    """Transcribe with faster-whisper (lazy import; QA-only dependency).
    model_size is 'small' or 'medium' — the QA harness always runs both,
    because a number both models hear the same way is a number the
    audience will hear correctly."""
    from faster_whisper import WhisperModel
    m = WhisperModel(model_size, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio_path, language="zh", beam_size=5)
    return "".join(s.text for s in segs)


def check_numbers(audio_path, expected, models=("small", "medium")):
    """expected: {token: [accepted transcript variants]}.
    Returns {model: {token: bool}} — a token passes a model if any of
    its variants appears in that model's transcript."""
    result = {}
    for size in models:
        text = asr_transcribe(audio_path, size).replace(" ", "")
        result[size] = {
            tok: any(v.replace(" ", "") in text for v in variants)
            for tok, variants in expected.items()
        }
    return result
