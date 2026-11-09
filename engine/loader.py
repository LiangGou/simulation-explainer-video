#!/usr/bin/env python3
"""ENGINE LAYER — episode loading.

An episode is a folder containing episode.py (see SKILL.md, "The
episode contract"). This loader puts the project root on sys.path (so
the episode can `from engine... import ...`) and imports the module
from its file path, whatever the folder is called.
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_episode(episode_dir):
    episode_dir = os.path.abspath(episode_dir)
    path = os.path.join(episode_dir, "episode.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"no episode.py in {episode_dir}")
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    name = "episode_" + os.path.basename(episode_dir).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.__episode_dir__ = episode_dir
    return mod


def load_timeline(episode_dir):
    import json
    path = os.path.join(episode_dir, "timeline.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"no timeline.json in {episode_dir} — run engine.synth first")
    with open(path) as f:
        return json.load(f)
