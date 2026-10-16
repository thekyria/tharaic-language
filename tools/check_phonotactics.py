#!/usr/bin/env python3
"""List Greek-script words that break Tharaic syllable rules.

Rules (see docs/phonology.md): at most one consonant in a syllable onset,
at most one in a coda, and a coda may only be ν, σ, ρ, λ, μ or κ.

By default the everyday rules apply, which also allow an onset of
obstruent + ρ/λ, the construct ending -ιτ and the loans listed in
LOANS (see docs/history.md). With --chant, only the strict rules apply.

Usage:
    python3 tools/check_phonotactics.py [--chant] [--strict] [files...]

Defaults to docs/*.md. With --strict, exits 1 when anything is found.
"""
import glob
import re
import sys
import unicodedata

VOWELS = set("αεηιουωᾱῡ")
CODA = set("νσςρλμκ")
DOUBLE = {"ξ": "κσ", "ψ": "πσ"}
OBSTRUENTS = set("πτκβδγφθχσζϸϙϝ")
LIQUIDS = set("ρλ")
ACCENTS = set("\u0300\u0301\u0313\u0314\u0342\u0345")  # grave, acute, breathings, circumflex, iota subscript
# Loans that keep a foreign cluster in everyday speech (docs/history.md, "Later loans")
LOANS = {"ξενος", "επτα"}
WORD = re.compile("[Ͱ-Ͽἀ-῿]+")


def normalize(word):
    word = word.lower()
    return "".join(DOUBLE.get(c, c) for c in word)


def onset_ok(run, chant):
    if len(run) <= 1:
        return True
    return not chant and len(run) == 2 and run[0] in OBSTRUENTS and run[1] in LIQUIDS


def problems(word, check_start=True, check_end=True, chant=False):
    """Return a list of rule violations for one word."""
    if not chant and word.lower().replace("ς", "σ") in {w.replace("ς", "σ") for w in LOANS}:
        return []
    if any(c in ACCENTS for c in unicodedata.normalize("NFD", word)):
        return []  # an accented citation from real Greek; Tharaic writes no accents
    w = normalize(word)
    if not any(c in VOWELS for c in w):
        return []  # a root, a bare letter, or a cluster example
    runs = re.findall("[αεηιουωᾱῡ]+|[^αεηιουωᾱῡ]+", w)
    found = []
    for i, run in enumerate(runs):
        if run[0] in VOWELS:
            continue
        first, last = i == 0, i == len(runs) - 1
        if first:
            if check_start and not onset_ok(run, chant):
                found.append(f"initial cluster {run}-")
        elif last:
            construct = not chant and run == "τ" and runs[i - 1].endswith("ι")
            if check_end and (len(run) > 1 or run not in CODA) and not construct:
                found.append(f"final -{run}")
        elif onset_ok(run, chant):
            continue
        elif run[0] in CODA and onset_ok(run[1:], chant):
            continue
        elif len(run) > 2 or not onset_ok(run[1:], chant):
            found.append(f"cluster -{run}-")
        else:
            found.append(f"coda {run[0]} in -{run}-")
    return found


def scan(paths, chant=False):
    seen = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = unicodedata.normalize("NFC", line)
                for m in WORD.finditer(line):
                    before = line[m.start() - 1] if m.start() else ""
                    after = line[m.end()] if m.end() < len(line) else ""
                    found = problems(m.group(), before != "-", after != "-", chant)
                    if found and m.group().lower() not in seen:
                        seen[m.group().lower()] = (path, n, m.group(), found)
    return list(seen.values())


if __name__ == "__main__":
    args = sys.argv[1:]
    strict = "--strict" in args
    chant = "--chant" in args
    paths = [a for a in args if not a.startswith("--")] or sorted(glob.glob("docs/*.md"))
    results = scan(paths, chant)
    for path, n, word, found in results:
        print(f"{path}:{n}: {word} — {'; '.join(found)}")
    print(f"{len(results)} word(s) with violations")
    sys.exit(1 if strict and results else 0)
