#!/usr/bin/env python3
"""Check data/lexicon.yaml and generate docs/lexicon.md from it.

Usage:
    python3 tools/build_lexicon.py           # check, then write docs/lexicon.md
    python3 tools/build_lexicon.py --check   # check, and fail if docs/lexicon.md is out of date

Each entry in data/lexicon.yaml has these fields:

    greek     the word in Greek script. Adjectives give both forms: "καλος / καλον"
    pos       noun, verb, adj, adv, prep, conj, particle, question, pron or num
    meaning   English meaning
    layer     native (inherited, built on a root), phoenician or greek (later loans)
    theme     which section of the lexicon it belongs to (see THEMES below)
    gender    nouns only: AN or IN
    stem      nouns only: O, A, ON, AR, EUS, ON-PL (old plural used as a collective) or irregular
    cases     prepositions only: the case(s) it takes, e.g. "LOC, ACC"
    root      optional: consonantal root, e.g. "Ν-Ϝ"
    source    optional: etymology note
    chant     the chant form; required when the word breaks the strict chant rules
    note      optional: extra remark, shown after the meaning
    value     numbers only: the numeric value, used for ordering
    late      optional, "yes": a native word formed after the sound changes in
              docs/history.md (e.g. with the productive suffix -υτον), so they do not apply
    roman     optional: romanization, when the automatic one is not wanted

The file uses a small subset of YAML (a list of flat mappings with
double-quoted values), so no YAML library is needed.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from greek import to_greek, to_roman  # noqa: E402
from check_phonotactics import problems, OBSTRUENTS, VOWELS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "lexicon.yaml")
OUT = os.path.join(ROOT, "docs", "lexicon.md")

THEMES = [
    ("sea", "The Sea & Navigation"),
    ("weather", "Weather & Sea Life"),
    ("nature", "Nature & Elements"),
    ("land", "Land, Plants & Animals"),
    ("directions", "Cardinal Directions"),
    ("body", "The Body, Health & Sickness"),
    ("people", "People, Kinship & Society"),
    ("home", "House, Food & Clothing"),
    ("trade", "Trade & Craft"),
    ("city", "City, Law & Power"),
    ("ritual", "Ritual, Belief & Abstract"),
    ("mind", "Mind, Speech & Feeling"),
    ("time", "Time, Calendar & Stars"),
    ("numbers", "Numbers"),
    ("verbs", "Core Verbs"),
    ("motion", "Movement & Position"),
    ("adjectives", "Adjectives & Colors"),
    ("function", "Function Words"),
]
POS = {"noun": "n.", "verb": "v.", "adj": "adj.", "prep": "prep.", "conj": "conj.",
       "particle": "particle", "question": "question word", "pron": "pron.", "num": "num.", "adv": "adv."}
FUNCTION_ORDER = ["pron", "prep", "conj", "particle", "question", "adv"]
LAYERS = {"native": "native", "phoenician": "Phoenician", "greek": "Greek"}
STEMS = {"O": ("AN", "ος", "O-stem"), "A": ("AN", ("ᾱ", "α"), "A-stem"), "EUS": ("AN", "ευς", "-ευς"),
         "ON": ("IN", "ον", "ON-stem"), "AR": ("IN", "αρ", "AR-stem"),
         "ON-PL": ("IN", "α", "ON-stem plural"), "irregular": (None, "", "irregular")}
# Alphabetical order, with the extra letters at their historical places
ALPHABET = "αᾱβγδεϝζͱηθιϳκλμνξοπϙρσςϸτυῡφχψω"
DIPHTHONGS = {"αι", "αυ", "ει", "ου", "ευ", "οι"}


def parse(path):
    entries, cur = [], None
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r'^(- |  )([a-z]+): "((?:[^"\\]|\\.)*)"\s*$', line)
            if not m:
                sys.exit(f"{path}:{n}: cannot parse: {line.rstrip()}")
            lead, key, val = m.groups()
            val = re.sub(r"\\(.)", r"\1", val)
            if lead == "- ":
                cur = {"_line": n}
                entries.append(cur)
            elif cur is None:
                sys.exit(f"{path}:{n}: field outside an entry")
            if key in cur:
                sys.exit(f"{path}:{n}: duplicate field {key}")
            cur[key] = val
    return entries


def romanize(e):
    if "roman" in e:
        return e["roman"]
    r = to_roman(e["greek"])
    if e["layer"] == "greek":
        # Greek-layer words write υ as y (συν syn), except in diphthongs and before a vowel
        r = re.sub(r"(?<![aeo])u(?![aeiouāēōū])", "y", r)
        r = re.sub(r"(?<![aeo])U(?![aeiouāēōū])", "Y", r)
    return r


def words(text):
    return [w for w in re.split(r"[ /…]+", text) if w]


def nuclei(word):
    """Vowel nuclei of a word as (start, end) spans, treating diphthongs as one."""
    w, spans, i = word.lower(), [], 0
    while i < len(w):
        if w[i] in VOWELS:
            j = i + 2 if w[i:i + 2] in DIPHTHONGS else i + 1
            spans.append((i, j))
            i = j
        else:
            i += 1
    return spans


def history_problems(word):
    """Native words should show changes 1 and 2 from docs/history.md."""
    w, ns, found = word.lower(), nuclei(word), []
    if len(ns) >= 2:
        s, e = ns[-2]
        if w[s:e] == "ᾱ" and s > 0 and w[s - 1] == "τ":
            found.append("τ before stressed ᾱ should be θ (change 1)")
    if len(ns) >= 3:
        s, e = ns[-3]
        if (e - s == 1 and w[s] in "ιυο" and s > 0 and w[s - 1] in OBSTRUENTS
                and e < len(w) and w[e] in "ρλ" and e + 1 < len(w) and w[e + 1] in VOWELS):
            found.append(f"pretonic {w[s]} between {w[s - 1]} and {w[e]} should be lost (change 2)")
    return found


def check(entries):
    errors, seen = [], {}
    themes = {k for k, _ in THEMES}
    for e in entries:
        where = f"{DATA}:{e['_line']}: {e.get('greek', '?')}"
        err = lambda msg: errors.append(f"{where}: {msg}")  # noqa: E731
        for k in ("greek", "pos", "meaning", "layer", "theme"):
            if k not in e:
                err(f"missing {k}")
        if any(k not in e for k in ("greek", "pos", "layer", "theme")):
            continue
        g, pos = e["greek"], e["pos"]
        if pos not in POS:
            err(f"unknown pos {pos}")
        if e["layer"] not in LAYERS:
            err(f"unknown layer {e['layer']}")
        if e["theme"] not in themes:
            err(f"unknown theme {e['theme']}")
        key = (g, pos)
        if key in seen:
            err(f"duplicate of line {seen[key]}")
        seen[key] = e["_line"]
        if to_greek(romanize(e)) != g:
            err(f"romanization {romanize(e)!r} does not convert back")
        if pos == "noun":
            stem, gender = e.get("stem"), e.get("gender")
            if gender not in ("AN", "IN"):
                err("noun needs gender AN or IN")
            if stem not in STEMS:
                err(f"noun needs a stem from {', '.join(STEMS)}")
            else:
                want_gender, ending, _ = STEMS[stem]
                if not g.endswith(ending):
                    err(f"{stem} noun should end in {ending}")
                if want_gender and gender != want_gender and "note" not in e:
                    err(f"{stem} nouns are {want_gender}; explain the exception in a note")
        elif pos == "verb" and not g.endswith(("ειν", "σθαι")):
            err("verb should be an infinitive in -ειν or (middle) -σθαι")
        elif pos == "adj" and not re.fullmatch(r"\S+(ος|ᾱς|ᾱ|υς) / \S+ον", g):
            err("adjective should be 'AN / IN', e.g. 'καλος / καλον'")
        elif pos == "prep" and "cases" not in e:
            err("preposition needs cases")
        elif pos == "num" and "value" not in e:
            err("number needs value")
        strict_ok = True
        for w in words(g):
            body = w.strip("-")
            start, end = not w.startswith("-"), not w.endswith("-")
            for p in problems(body, start, end):
                err(p)
            if problems(body, start, end, chant=True):
                strict_ok = False
            if e["layer"] == "native" and e.get("late") != "yes":
                for p in history_problems(body):
                    err(p)
        if "chant" in e:
            for w in words(e["chant"]):
                for p in problems(w.strip("-"), chant=True):
                    err(f"chant form: {p}")
        elif not strict_ok:
            err("breaks the chant rules, so it needs a chant form")
    return errors


def sort_key(text):
    return [ALPHABET.index(c) if c in ALPHABET else len(ALPHABET) for c in text.lower()]


def grammar(e):
    pos = e["pos"]
    if pos == "noun":
        return f"n. {e['gender']}, {STEMS[e['stem']][2]}"
    if pos == "verb":
        return "v. (middle)" if e["greek"].endswith("σθαι") else "v."
    if pos == "prep":
        return f"prep. + {e['cases']}"
    return POS[pos]


def origin_text(e):
    label, src = LAYERS[e["layer"]], e.get("source")
    if not src:
        return label
    if src.startswith(label):
        return src
    return f"{label} ({src})"


def render(entries):
    out = [
        "# Lexicon",
        "",
        "[← Overview](../README.md)",
        "",
        "<!-- Generated from data/lexicon.yaml by tools/build_lexicon.py. Edit the YAML, not this file. -->",
        "",
        f"{len(entries)} words, grouped by theme and sorted in Tharaic alphabetical order "
        f"(*{' '.join(c for c in ALPHABET if c not in 'ᾱῡς')}*: the extra letters sit at their historical places).",
        "",
        "- **Root** is the consonantal root for words built in the [older layer](word-building.md#older-layer-patterns-on-roots).",
        "- **Origin**: *native* words are inherited and built on a root; *Phoenician* and *Greek* words are later loans "
        "that keep their source shape. A source note marked *cf.* compares a native word with its Semitic relative.",
        "- **Chant** gives the form used in chant and sacred speech, where it differs ([History § The chant register](history.md#3-the-chant-register)).",
        "- In Greek-layer words, υ is romanized *y* (*συν* syn), except in diphthongs and before a vowel (*κυανος* kuanos).",
        "",
    ]
    by_theme = {k: [] for k, _ in THEMES}
    for e in entries:
        by_theme[e["theme"]].append(e)
    for key, title in THEMES:
        items = by_theme[key]
        if not items:
            continue
        if key == "numbers":
            items.sort(key=lambda e: int(e["value"]))
        elif key == "function":
            items.sort(key=lambda e: (FUNCTION_ORDER.index(e["pos"]), sort_key(e["greek"])))
        else:
            items.sort(key=lambda e: sort_key(e["greek"]))
        out += [f"## {title}", "", "| Tharaic | Romanized | Root | Grammar | Meaning | Origin | Chant |",
                "|---------|-----------|------|---------|---------|--------|-------|"]
        for e in items:
            meaning = e["meaning"] + (f" — {e['note']}" if "note" in e else "")
            origin = origin_text(e)
            chant = f"*{e['chant']}*" if "chant" in e else ""
            out.append(f"| *{e['greek']}* | {romanize(e)} | {e.get('root', '')} | {grammar(e)} | "
                       f"{meaning} | {origin} | {chant} |")
        out.append("")
    return "\n".join(out)


def main():
    entries = parse(DATA)
    errors = check(entries)
    for line in errors:
        print(line)
    if errors:
        sys.exit(f"{len(errors)} problem(s) in {DATA}")
    text = render(entries)
    if "--check" in sys.argv[1:]:
        with open(OUT, encoding="utf-8") as f:
            if f.read() != text:
                sys.exit(f"{OUT} is out of date; run python3 tools/build_lexicon.py")
        print(f"{len(entries)} entries OK; {OUT} is up to date")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{len(entries)} entries OK; wrote {OUT}")


if __name__ == "__main__":
    main()
