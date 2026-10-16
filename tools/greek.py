#!/usr/bin/env python3
"""Convert romanized Tharaic to Greek script.

Usage:
    python3 tools/greek.py nāvei navos epi thāros
    echo "Kalos velos!" | python3 tools/greek.py
"""
import re
import sys

DIGRAPHS = {"ph": "φ", "th": "θ", "kh": "χ", "sh": "ϸ", "gh": "ϙ"}
LETTERS = {
    "a": "α", "ā": "ᾱ", "b": "β", "d": "δ", "e": "ε", "ē": "η", "g": "γ",
    "h": "ͱ", "i": "ι", "k": "κ", "l": "λ", "m": "μ", "n": "ν", "o": "ο",
    "ō": "ω", "p": "π", "r": "ρ", "s": "σ", "t": "τ", "u": "υ", "ū": "ῡ",
    "v": "ϝ", "x": "ξ", "z": "ζ",
}
VOWELS = set("aāeēioōuū")
GREEK = "Ͱ-Ͽἀ-῿"


def to_greek(text):
    """Transliterate romanized text; anything that is not a Tharaic letter passes through."""
    out, i = [], 0
    while i < len(text):
        c = text[i]
        lower = c.lower()
        pair = text[i:i + 2].lower()
        if pair in DIGRAPHS:
            g, i = DIGRAPHS[pair], i + 2
        elif lower == "y":
            # y before a vowel is the consonant /j/; otherwise it is the vowel of Greek loans (συν, πυρα)
            g, i = ("ϳ" if text[i + 1:i + 2].lower() in VOWELS else "υ"), i + 1
        elif lower in LETTERS:
            g, i = LETTERS[lower], i + 1
        else:
            out.append(c)
            i += 1
            continue
        out.append(g.upper() if c != lower else g)
    return re.sub(f"σ(?![\\w{GREEK}])", "ς", "".join(out))


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    print(to_greek(text).rstrip("\n"))
