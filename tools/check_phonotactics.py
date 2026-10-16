#!/usr/bin/env python3
"""List Greek-script words that break Tharaic syllable rules.

Rules (see docs/phonology.md): at most one consonant in a syllable onset,
at most one in a coda, and a coda may only be ν, σ, ρ, λ, μ or κ.

Usage:
    python3 tools/check_phonotactics.py [--strict] [files...]

Defaults to docs/*.md. With --strict, exits 1 when anything is found.
"""
import glob
import re
import sys
import unicodedata

VOWELS = set("αεηιουωᾱῡ")
CODA = set("νσςρλμκ")
DOUBLE = {"ξ": "κσ", "ψ": "πσ"}
WORD = re.compile("[Ͱ-Ͽἀ-῿]+")


def normalize(word):
    word = word.lower()
    return "".join(DOUBLE.get(c, c) for c in word)


def problems(word, check_start=True, check_end=True):
    """Return a list of rule violations for one word."""
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
            if check_start and len(run) > 1:
                found.append(f"initial cluster {run}-")
        elif last:
            if check_end and (len(run) > 1 or run not in CODA):
                found.append(f"final -{run}")
        elif len(run) > 2:
            found.append(f"cluster -{run}-")
        elif len(run) == 2 and run[0] not in CODA:
            found.append(f"coda {run[0]} in -{run}-")
    return found


def scan(paths):
    seen = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = unicodedata.normalize("NFC", line)
                for m in WORD.finditer(line):
                    before = line[m.start() - 1] if m.start() else ""
                    after = line[m.end()] if m.end() < len(line) else ""
                    found = problems(m.group(), before != "-", after != "-")
                    if found and m.group().lower() not in seen:
                        seen[m.group().lower()] = (path, n, m.group(), found)
    return list(seen.values())


if __name__ == "__main__":
    args = sys.argv[1:]
    strict = "--strict" in args
    paths = [a for a in args if a != "--strict"] or sorted(glob.glob("docs/*.md"))
    results = scan(paths)
    for path, n, word, found in results:
        print(f"{path}:{n}: {word} — {'; '.join(found)}")
    print(f"{len(results)} word(s) with violations")
    sys.exit(1 if strict and results else 0)
