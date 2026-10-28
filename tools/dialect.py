#!/usr/bin/env python3
"""Turn coastal (standard) Tharaic into the island dialect.

Usage:
    python3 tools/dialect.py "Ϝα-λεκει: «Βαλ ϸα νᾱϝομεν προς λιμᾱν.»"
    echo "τρια ναϝιμ" | python3 tools/dialect.py

The island dialect (docs/dialects.md) differs from the coastal standard by
regular rules, applied here in order:

1. Construct forms keep their old final vowel: -ιλ, -ιτ, -υλ -> -ιλα, -ιτα, -υλα.
2. Words that break the strict syllable rules take their chant form, as given
   in data/lexicon.yaml (τρια -> τιρια, αστρος -> αστορος). Inflected forms use
   the chant form of their stem; a word with no match breaks its clusters with
   a copy of the following vowel, the rule for loans.
3. ϸ becomes σ.

Words that still break the strict rules are listed on stderr.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexicon import DATA, parse, words  # noqa: E402
from check_phonotactics import CODA, VOWELS, normalize, problems  # noqa: E402

WORD = re.compile("[Ͱ-Ͽἀ-῿]+")
SHORT = {"ᾱ": "α", "η": "ε", "ω": "ο", "ῡ": "υ"}


def chant_rules():
    """(standard stem, chant stem) pairs from the lexicon, longest first."""
    rules = {}
    for e in parse(DATA):
        if "chant" not in e:
            continue
        for s, c in zip(words(e["greek"]), words(e["chant"])):
            s, c = s.strip("-"), c.strip("-")
            rules[s] = c
            for k in (1, 2):
                if len(s) - k >= 3 and s[-k:] == c[-k:]:
                    rules.setdefault(s[:-k], c[:-k])
    return sorted(rules.items(), key=lambda r: -len(r[0]))


RULES = chant_rules()


def echo(word):
    """Break clusters with a copy of the following vowel (docs/history.md § 3)."""
    runs = re.findall("[αεηιουωᾱῡ]+|[^αεηιουωᾱῡ]+", normalize(word))
    out = []
    for i, run in enumerate(runs):
        if run[0] in VOWELS or len(run) == 1 or i == len(runs) - 1:
            out.append(run)
            continue
        v = SHORT.get(runs[i + 1][0], runs[i + 1][0])
        keep = run[0] if i > 0 and run[0] in CODA else ""
        out.append(keep + v.join(run[len(keep):]))
    return "".join(out).replace("κσ", "ξ").replace("πσ", "ψ")


def island_word(word):
    w = word.lower().replace("ς", "σ")
    if re.search("(ιλ|ιτ|υλ)$", w):
        w += "α"
    if problems(w, chant=True):
        for s, c in RULES:
            if w.startswith(s.replace("ς", "σ")):
                w = c.replace("ς", "σ") + w[len(s):]
                break
        else:
            w = echo(w)
    w = re.sub("σ$", "ς", w.replace("ϸ", "σ"))
    return w[0].upper() + w[1:] if word[0].isupper() else w


def island(text):
    return WORD.sub(lambda m: island_word(m.group()), text)


def main():
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    out = island(text)
    print(out)
    left = {w for w in WORD.findall(out) if problems(w, chant=True)}
    if left:
        print("still breaking the strict rules: " + ", ".join(sorted(left)), file=sys.stderr)


if __name__ == "__main__":
    main()
