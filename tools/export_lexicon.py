#!/usr/bin/env python3
"""Export data/lexicon.yaml as JSON for the website's English → Tharaic lookup.

Usage:
    python3 tools/export_lexicon.py            # print the JSON
    python3 tools/export_lexicon.py out.json   # write it to a file

The website build (website/hooks.py) calls lexicon_json() directly. The English
keys are the same as in docs/english-index.md.

Format:
    {"entries": [{"g": greek, "r": romanized, "p": part of speech, "gr": grammar,
                  "m": meaning, "reg": register, "dia": dialect, "sec": lexicon anchor}, ...],
     "keys": {"english key (lowercase)": [[entry number, position of the key in the entry], ...]}}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexicon import DATA, THEMES, anchor, english_keys, grammar, parse, romanize  # noqa: E402


def lexicon_data(entries=None):
    entries = parse(DATA) if entries is None else entries
    titles = dict(THEMES)
    out, keys = [], {}
    for n, e in enumerate(entries):
        item = {
            "g": e["greek"],
            "r": romanize(e),
            "p": e["pos"],
            "gr": grammar(e).replace("*", ""),
            "m": e["meaning"] + (f" — {e['note']}" if "note" in e else ""),
            "sec": anchor(titles[e["theme"]]),
        }
        for field, short in (("register", "reg"), ("dialect", "dia")):
            if field in e:
                item[short] = e[field]
        out.append(item)
        for pos, k in enumerate(english_keys(e)):
            keys.setdefault(k.lower(), []).append([n, pos])
    return {"entries": out, "keys": keys}


def lexicon_json(entries=None):
    return json.dumps(lexicon_data(entries), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    text = lexicon_json()
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
