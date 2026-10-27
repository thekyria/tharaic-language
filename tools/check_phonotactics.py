#!/usr/bin/env python3
"""List Greek-script words that break Tharaic syllable rules.

Rules (see docs/phonology.md): at most one consonant in a syllable onset,
at most one in a coda, and a coda may only be ν, σ, ρ, λ, μ or κ.

By default the everyday rules apply, which also allow an onset of
obstruent + ρ/λ, the construct ending -ιτ and the loans listed in
LOANS (see docs/history.md). With --chant, only the strict rules apply.
With --high, the rules of the high register apply: learned Doric loans
keep the clusters of their source (docs/registers.md).

In the default scan, words that break the everyday rules but fit the
high-register rules are listed separately and are not counted as
violations: they should be Doric loans.

Usage:
    python3 tools/check_phonotactics.py [--chant | --high] [--strict] [files...]

Defaults to docs/*.md. With --strict, exits 1 when a violation is found.
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
STOPS = set("πτκβδγφθχ")
NASALS = set("μν")
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


def high_onset_ok(run):
    """Onsets of the high register: those of the Doric source (docs/registers.md)."""
    if len(run) <= 1:
        return True
    if len(run) == 3:
        return run[0] == "σ" and run[1] in STOPS and run[2] in LIQUIDS
    a, b = run
    return (a in OBSTRUENTS and b in LIQUIDS               # τρ, κλ
            or a == "σ" and (b in STOPS or b == "μ")       # στ, σχ, σμ
            or a in "πκφχ" and b in "τθ"                    # πτ, κτ, φθ, χθ
            or a in STOPS and b in NASALS or run == "μν"   # γν, θν, τμ, μν
            or run in ("κσ", "πσ"))                        # ξ, ψ


def high_problems(word, check_start=True, check_end=True):
    runs = re.findall("[αεηιουωᾱῡ]+|[^αεηιουωᾱῡ]+", normalize(word))
    found = []
    for i, run in enumerate(runs):
        if run[0] in VOWELS:
            continue
        if i == 0:
            if check_start and not high_onset_ok(run):
                found.append(f"initial cluster {run}-")
        elif i == len(runs) - 1:
            if check_end and run not in CODA | {"κσ", "πσ"} and not (run == "τ" and runs[i - 1].endswith("ι")):
                found.append(f"final -{run}")
        elif not (high_onset_ok(run) or len(run) <= 4 and high_onset_ok(run[1:])):
            found.append(f"cluster -{run}-")
    return found


def problems(word, check_start=True, check_end=True, chant=False, high=False):
    """Return a list of rule violations for one word."""
    if not chant and word.lower().replace("ς", "σ") in {w.replace("ς", "σ") for w in LOANS}:
        return []
    if any(c in ACCENTS for c in unicodedata.normalize("NFD", word)):
        return []  # an accented citation from real Greek; Tharaic writes no accents
    w = normalize(word)
    if not any(c in VOWELS for c in w):
        return []  # a root, a bare letter, or a cluster example
    if high and not chant:
        return high_problems(word, check_start, check_end)
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


def scan(paths, chant=False, high=False):
    seen, high_only = {}, {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = unicodedata.normalize("NFC", line)
                for m in WORD.finditer(line):
                    before = line[m.start() - 1] if m.start() else ""
                    after = line[m.end()] if m.end() < len(line) else ""
                    edges = (before != "-", after != "-")
                    found = problems(m.group(), *edges, chant, high)
                    key = m.group().lower()
                    if not found or key in seen or key in high_only:
                        continue
                    if not chant and not high and not problems(m.group(), *edges, high=True):
                        high_only[key] = (path, n, m.group(), found)
                    else:
                        seen[key] = (path, n, m.group(), found)
    return list(seen.values()), list(high_only.values())


if __name__ == "__main__":
    args = sys.argv[1:]
    strict = "--strict" in args
    chant = "--chant" in args
    high = "--high" in args
    paths = [a for a in args if not a.startswith("--")] or sorted(glob.glob("docs/*.md"))
    results, high_only = scan(paths, chant, high)
    if high_only:
        print("High-register shapes (allowed only in learned Doric loans):")
        for path, n, word, found in high_only:
            print(f"  {path}:{n}: {word} — {'; '.join(found)}")
    for path, n, word, found in results:
        print(f"{path}:{n}: {word} — {'; '.join(found)}")
    print(f"{len(results)} word(s) with violations")
    sys.exit(1 if strict and results else 0)
