#!/usr/bin/env python3
"""Export data/lexicon.yaml as JSON for the website.

Usage:
    python3 tools/export_lexicon.py                  # print the lexicon JSON
    python3 tools/export_lexicon.py out.json         # write it to a file
    python3 tools/export_lexicon.py --forms out.json # write the word forms instead

The website build (website/hooks.py) calls lexicon_json() and forms_json() directly.

The lexicon, for the English → Tharaic lookup; the English keys are the same as
in docs/english-index.md:
    {"entries": [{"g": greek, "r": romanized, "p": part of speech, "gr": grammar,
                  "m": meaning, "reg": register, "dia": dialect, "sec": lexicon anchor}, ...],
     "keys": {"english key (lowercase)": [[entry number, position of the key in the entry], ...]}}

The word forms, for analyzing Tharaic words: every form tools/inflect.py
generates, written with medial σ throughout, as in its Index:
    {"lemmas": [[headword, [entry numbers], name meaning or ""], ...],
     "tags": ["AOR.3SG", ...],
     "forms": {"form": [[lemma number, tag number], ...]},
     "possessive": {"ι": "my", ...}, "object": {"νι": "me", ...}, "prefixes": ["ϝα", ...]}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexicon import DATA, THEMES, anchor, english_keys, grammar, head, parse, romanize  # noqa: E402
from inflect import OBJECT, POSSESSIVE, PREFIXES, Index, load_names  # noqa: E402

# Meanings of the enclitics in tools/inflect.py (docs/morphology.md, Pronouns & Enclitics)
POSSESSIVE_MEANING = {"ι": "my", "κα": "your (sg.)", "υ": "his, her", "α": "its", "εν": "our",
                      "κεμ": "your (pl.)", "ιμ": "their (animate)", "ομ": "their (inanimate)"}
OBJECT_MEANING = {"νι": "me", "τα": "you (sg.)", "υ": "him, her", "α": "it", "ιμ": "them (animate)",
                  "ομ": "them (inanimate)", "νεν": "us", "τεμ": "you (pl.)", "ναιν": "us two",
                  "αιν": "them two"}


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


def forms_data(entries=None, names=None):
    entries = parse(DATA) if entries is None else entries
    names = load_names() if names is None else names
    by_head = {}
    for n, e in enumerate(entries):
        by_head.setdefault(head(e), []).append(n)
    name_meaning = {nm["greek"]: nm["meaning"] for nm in names}
    lemmas, lemma_no, tags, tag_no, forms = [], {}, [], {}, {}
    for form, analyses in Index(entries, names).forms.items():
        out = []
        for lemma, tag in analyses:
            if lemma not in lemma_no:
                lemma_no[lemma] = len(lemmas)
                lemmas.append([lemma, by_head.get(lemma, []), name_meaning.get(lemma, "") if lemma not in by_head else ""])
            if tag not in tag_no:
                tag_no[tag] = len(tags)
                tags.append(tag)
            pair = [lemma_no[lemma], tag_no[tag]]
            if pair not in out:
                out.append(pair)
        forms[form] = out
    return {"lemmas": lemmas, "tags": tags, "forms": forms, "possessive": POSSESSIVE_MEANING,
            "object": OBJECT_MEANING, "prefixes": list(PREFIXES)}


def forms_json(entries=None, names=None):
    return json.dumps(forms_data(entries, names), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    args = sys.argv[1:]
    text = lexicon_json()
    if args and args[0] == "--forms":
        text, args = forms_json(), args[1:]
    if args:
        with open(args[0], "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
