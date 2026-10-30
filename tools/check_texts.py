#!/usr/bin/env python3
"""Check that every word of the Tharaic texts is a form of a lexicon word or a name.

Usage:
    python3 tools/check_texts.py [--strict] [files...]

Each Greek-script word in the files must be an inflected form that
tools/inflect.py can produce from data/lexicon.yaml or data/names.tsv,
possibly with the prefixes ϝα-, ϸε-, ͱα-, object enclitics after a hyphen
(ελεκε-ιμ, προς-υ) or a possessive enclitic (ναϝᾱι, ͱοδονκα).

Skipped: accented citations of real Greek, roots (Ν-Ϝ, Α-Λ-Μ), single letters, word parts written with a leading or trailing hyphen (-ιλ, ϝα-), and
starred forms (\\*βᾱσιλιλ), which mark something as wrong or reconstructed.

A line can also name words to skip on that line, in a comment that does not
show on the rendered page, for older forms or words split into their parts:
    … the participle as νᾱϝον / νᾱϝουσα … <!-- check_texts: skip νᾱϝουσα -->

Defaults to the texts listed in TEXTS. With --strict, exits 1 when a word
is unknown.
"""
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexicon import ROOT  # noqa: E402
from check_phonotactics import ACCENTS, VOWELS  # noqa: E402
from inflect import Index  # noqa: E402

# The texts and the grammar pages. registers.md and history.md also show older and
# deliberately wrong forms, and dialects.md shows island forms, so they are not checked.
TEXTS = ["texts.md", "proverbs.md", "sacred.md", "stories.md", "calendar.md", "gospels.md", "mark-1.md",
         "syntax.md", "word-building.md", "morphology.md"]
LETTERS = "Ͱ-Ͽἀ-῿"
TOKEN = re.compile(f"[{LETTERS}]+(?:-[{LETTERS}]+)*")
SKIP = re.compile(r"<!-- check_texts: skip (.*?) -->")


def tokens(line):
    """(token, column) for each Tharaic word worth checking in a line."""
    for m in TOKEN.finditer(line):
        word, start, end = m.group(), m.start(), m.end()
        before, after = line[max(0, start - 2):start], line[end:end + 1]
        if before.endswith("-") or after == "-" or "\\" in before:
            continue
        if any(c in ACCENTS for c in unicodedata.normalize("NFD", word)):
            continue
        parts = word.split("-")
        if not any(c in VOWELS for c in word.lower()) or all(len(p) == 1 for p in parts):
            continue  # a root such as Ν-Ϝ or Α-Λ-Μ, or a letter cited as a letter
        yield word, start


def scan(paths, index):
    unknown = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = unicodedata.normalize("NFC", line)
                skip = {w for m in SKIP.finditer(line) for w in m.group(1).split()}
                for word, _ in tokens(SKIP.sub("", line)):
                    if word not in skip and not index.analyze(word):
                        unknown.append((path, n, word))
    return unknown


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")] or [os.path.join(ROOT, "docs", t) for t in TEXTS]
    unknown = scan(paths, Index())
    for path, n, word in unknown:
        print(f"{os.path.relpath(path)}:{n}: {word}")
    print(f"{len(unknown)} unknown word(s) in {len(paths)} file(s)")
    sys.exit(1 if strict and unknown else 0)


if __name__ == "__main__":
    main()
