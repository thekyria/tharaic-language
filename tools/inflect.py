#!/usr/bin/env python3
"""Inflect Tharaic words from data/lexicon.yaml, and analyze inflected forms.

Usage:
    python3 tools/inflect.py ναϝᾱ λεκειν     # print the paradigms of lexicon words
    python3 tools/inflect.py --parse εβλεψε  # analyze forms: lexicon word and grammar
    python3 tools/inflect.py --tables        # regenerate the paradigm tables in docs/
    python3 tools/inflect.py --check         # fail if those tables are out of date

The rules are those of docs/morphology.md and docs/word-building.md:

- Nouns decline by stem class (O, A, ON, AR, -ευς, the ON-PL collectives).
  Doric loans (layer doric) take Doric endings in the five Greek cases and
  Tharaic endings in the sea cases and the dual. Native-style nouns also have
  a construct form (-ιλ, -ιτ, -υλ).
- Adjectives and participles decline like καλος, in both genders, and form
  the comparative -οτερος and superlative -οτατος.
- Verbs have the present, the aorist (augment ε-, or a lengthened first
  vowel), the middle voice, infinitive, imperative and four participles.
  Doric verbs take 1st plural -μες (middle -μεσθα) and 3rd plural -ντι, and
  their aorist stem comes from the lexicon.
- Proper names from data/names.tsv decline like nouns of their class.

Tables in docs/ are regenerated between the markers
    <!-- inflect: KIND WORD -->  ...  <!-- /inflect -->
where KIND is noun, eus, adjective, present, aorist, middle-present,
middle-aorist or doric-verb.

What the grammar leaves open, the tool decides as follows: the dual of
inanimate adjectives is that of the ON-stem (-οιν); native verbs that begin
with a vowel take the Doric augment (lengthening); irregular nouns have no
paradigm beyond their headword.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexicon import DATA, ROOT, head, parse, romanize, words  # noqa: E402

NAMES = os.path.join(ROOT, "data", "names.tsv")
DOCS = os.path.join(ROOT, "docs")

CASES = ["NOM", "ACC", "GEN", "DAT", "VOC", "LOC", "INS", "ABL"]
NUMBERS = ["SG", "DU", "PL"]
VOWELS = set("αεηιουωᾱῡ")
LONG = {"α": "ᾱ", "ε": "η", "ο": "ω", "υ": "ῡ"}
SHORT = {v: k for k, v in LONG.items()}
DIPHTHONGS = ("αι", "αυ", "ει", "ευ", "οι", "ου")

# The three sea cases are the same in every class (Tharaic endings on the stem)
SEA = {"LOC": ("ελι", "ελιν", "ελις"), "INS": ("ομ", "ομιν", "ομις"), "ABL": ("αθα", "αθιν", "αθις")}

# Endings of the five Greek cases: (singular, dual, plural)
ENDINGS = {
    "O": {"NOM": ("ος", "ιν", "ιμ"), "ACC": ("ον", "ιν", "ονας"), "GEN": ("ι", "οιν", "ων"),
          "DAT": ("οι", "οιν", "οιμ"), "VOC": ("ε", "ιν", "ιμ")},
    "A": {"NOM": ("ᾱ", "ιν", "ιμ"), "ACC": ("ᾱν", "ιν", "ᾱνας"), "GEN": ("ις", "οιν", "ων"),
          "DAT": ("αι", "οιν", "αιμ"), "VOC": ("ε", "ιν", "ιμ")},
    "ON": {"NOM": ("ον", "οιν", "α"), "ACC": ("ον", "οιν", "α"), "GEN": ("ου", "οιν", "ων"),
           "DAT": ("οι", "οιν", "οιμ"), "VOC": ("ον", "οιν", "α")},
    # AR-stems keep -αρ- in every form, so their stem is the whole word
    "AR": {"NOM": ("", "ιν", "α"), "ACC": ("", "ιν", "α"), "GEN": ("ι", "ιν", "ων"),
           "DAT": ("οι", "ιν", "οιμ"), "VOC": ("", "ιν", "α")},
    # Doric classes (docs/morphology.md, "Doric nouns")
    "D-O": {"NOM": ("ος", "ιν", "οι"), "ACC": ("ον", "ιν", "ως"), "GEN": ("ω", "οιν", "ων"),
            "DAT": ("οι", "οιν", "οις"), "VOC": ("ε", "ιν", "οι")},
    "D-A": {"NOM": ("ᾱ", "ιν", "αι"), "ACC": ("ᾱν", "ιν", "ᾱς"), "GEN": ("ᾱς", "οιν", "ᾱν"),
            "DAT": ("αι", "οιν", "αις"), "VOC": ("ᾱ", "ιν", "αι")},
    "D-ON": {"NOM": ("ον", "ιν", "α"), "ACC": ("ον", "ιν", "α"), "GEN": ("ω", "οιν", "ων"),
             "DAT": ("οι", "οιν", "οις"), "VOC": ("ον", "ιν", "α")},
    "AS": {"NOM": ("ᾱς", "ιν", "αι"), "ACC": ("ᾱν", "ιν", "ᾱς"), "GEN": ("ᾱ", "οιν", "ᾱν"),
           "DAT": ("αι", "οιν", "αις"), "VOC": ("ᾱ", "ιν", "αι")},
    "IS": {"NOM": ("ις", "ιν", "ιες"), "ACC": ("ιν", "ιν", "ιας"), "GEN": ("ιος", "οιν", "ιων"),
           "DAT": ("ι", "οιν", "ισι"), "VOC": ("ι", "ιν", "ιες")},
}
CONSTRUCT = {"O": "ιλ", "A": "ιτ", "ON": "υλ", "AR": "υλ", "EUS": "ιλ"}
NOM_ENDING = {"O": "ος", "A": "ᾱ", "ON": "ον", "AR": "", "EUS": "ευς", "ON-PL": "α",
              "D-O": "ος", "D-A": "ᾱ", "D-ON": "ον", "AS": "ᾱς", "MA": "", "IS": "ις"}

# Possessive enclitics on nouns, and object enclitics after a hyphen (docs/morphology.md)
POSSESSIVE = ("ι", "κα", "υ", "α", "εν", "κεμ", "ιμ", "ομ")
OBJECT = ("νι", "τα", "υ", "α", "ιμ", "ομ", "νεν", "τεμ", "ναιν", "αιν")
# Prefixes written with a hyphen: narrative past, relative, question
PREFIXES = ("ϝα", "ϸε", "ͱα")

PERSONS = ["1SG", "2SG", "3SG", "DU", "1PL", "2PL", "3PL"]
PRESENT = ("ω", "εις", "ει", "ετον", "ομεν", "ετε", "ουσι")
AORIST = ("α", "ας", "ε", "ατον", "αμεν", "ατε", "αν")
MID_PRESENT = ("ομαι", "εσαι", "εται", "εσθον", "ομεθα", "εσθε", "ονται")
MID_AORIST = ("αμην", "ασο", "ατο", "ασθον", "αμεθα", "ασθε", "αντο")
DORIC_1PL = {"ομεν": "ομες", "αμεν": "αμες", "ομεθα": "ομεσθα", "αμεθα": "αμεσθα"}

# Irregular paradigms the rules cannot produce
SPECIAL = {
    # "to be": the present comes from ε(σ)-; κανειν gives the rest, and its own present
    # serves after ϸα and ϝα- (docs/morphology.md)
    "κανειν": [(f"PRES.{p} ε(σ)-", f) for p, f in zip(PERSONS, ("εμι", "εις", "εσι", "εστον", "εσμεν", "εστε", "εισι"))],
    # χαρις has the stem χαριτ- (docs/morphology.md, Doric nouns)
    "χαρις": [("NOM.SG", "χαρις"), ("ACC.SG", "χαριν"), ("GEN.SG", "χαριτος"), ("DAT.SG", "χαριτι"),
              ("VOC.SG", "χαρι"), ("NOM.PL", "χαριτες"), ("ACC.PL", "χαριτας"), ("GEN.PL", "χαριτων"),
              ("DAT.PL", "χαρισι"), ("VOC.PL", "χαριτες")]
    + [(f"{c}.{n}", "χαριτ" + x) for c in SEA for n, x in zip(NUMBERS, SEA[c])],
}


def first(text):
    return text.split(" / ")[0]


def final_sigma(w):
    return w[:-1] + "ς" if w.endswith("σ") else w


def medial_sigma(w):
    return w.replace("ς", "σ")


def noun_class(e):
    stem = e.get("stem")
    # A Doric word that has passed into everyday speech takes the ordinary endings: ισχολᾱ, GEN ισχολις
    if e.get("layer") == "doric" and e.get("register") != "everyday" and stem in ("O", "A", "ON"):
        return "D-" + stem
    return stem


def decline(base, cls, construct=True):
    """[(tag, form)] for a noun with nominative singular `base` of class `cls`."""
    out = []
    if cls == "ON-PL":
        stem = base[:-1]
        for case in CASES:
            ending = SEA[case][2] if case in SEA else {"GEN": "ων", "DAT": "οιμ"}.get(case, "α")
            out.append((f"{case}.PL", stem + ending))
        return out
    short_a = cls in ("A", "D-A") and base.endswith("α")
    if cls == "MA":
        stem = base + "τ"
        table = {"NOM": (base, stem + "ιν", stem + "α"), "ACC": (base, stem + "ιν", stem + "α"),
                 "VOC": (base, stem + "ιν", stem + "α"), "GEN": (stem + "ος", stem + "οιν", stem + "ων"),
                 "DAT": (stem + "ι", stem + "οιν", base + "σι")}
    else:
        if cls == "EUS":
            # O-stem endings on -εϝ-; only NOM -ευς and VOC -ευ differ (docs/word-building.md)
            stem = base[:-2] + "ϝ"
            table = {c: tuple(stem + x for x in v) for c, v in ENDINGS["O"].items()}
            table["NOM"] = (base,) + table["NOM"][1:]
            table["VOC"] = (base[:-1],) + table["VOC"][1:]
        else:
            ending = "α" if short_a else NOM_ENDING[cls]
            stem = base[:len(base) - len(ending)]
            table = {c: tuple(stem + x for x in v) for c, v in ENDINGS[cls].items()}
            if short_a and cls == "D-A":
                # short -α differs only in NOM, ACC, VOC singular: δοξα, δοξαν, δοξα
                for c, f in (("NOM", base), ("ACC", base + "ν"), ("VOC", base)):
                    table[c] = (f,) + table[c][1:]
            elif short_a:
                table["NOM"] = (base,) + table["NOM"][1:]
    for case in CASES:
        # a stem without a vowel (γᾱ "earth") takes the sea cases on the whole word: γᾱελι
        sea = stem if any(c in VOWELS for c in stem) else base
        forms = tuple(sea + x for x in SEA[case]) if case in SEA else table[case]
        for number, form in zip(NUMBERS, forms):
            out.append((f"{case}.{number}", final_sigma(form)))
    if construct and cls in CONSTRUCT:
        c = stem if cls == "O" and stem.endswith("ιλ") else stem + CONSTRUCT[cls]
        out.append(("CONSTR", c))
    return out


def adjective(an, inan, construct=True):
    """[(tag, form)] for an adjective or participle declined like καλος."""
    stem = inan[:-2]
    out = []
    for gender, cls, nom in (("AN", "O", an), ("IN", "ON", inan)):
        for tag, form in decline(stem + NOM_ENDING[cls], cls, construct):
            if tag == "NOM.SG":
                form = nom
            out.append((f"{gender}.{tag}", form))
    return out


def augment(stem):
    """The augmented aorist stem of a native verb (docs/morphology.md)."""
    if stem[0] not in VOWELS:
        return "ε" + stem
    if stem.startswith(DIPHTHONGS) or stem[0] == "ι":
        return stem
    return LONG.get(stem[0], stem[0]) + stem[1:]


def unaugment(aorist, stem):
    """The aorist stem without its augment, found by comparing it with the present stem:
    εποιησ- → ποιησ-, μετενοησ- → μετανοησ-, ᾱρξ- → αρξ-, ευξ- → ευξ-."""
    i = 0
    while i < min(len(aorist), len(stem)) and aorist[i] == stem[i]:
        i += 1
    if i == len(aorist):
        return aorist
    a, rest = aorist[i], aorist[i + 1:]
    if a == "ε" and rest:
        j = stem.find(rest[:2], i)
        if j >= 0:
            return stem[:j] + rest
    if a in SHORT and i < len(stem) and stem[i] == SHORT[a]:
        return aorist[:i] + SHORT[a] + rest
    return aorist


def conjugate(e):
    """[(tag, form)] for a verb entry."""
    inf = head(e)
    if inf in SPECIAL and e.get("pos") == "verb":
        out = list(SPECIAL[inf])
    else:
        out = []
    doric = e.get("layer") == "doric"
    middle_only = inf.endswith("σθαι")
    stem = inf[:-5] if middle_only else inf[:-3]
    aor = e.get("aorist")
    if aor:
        aor_middle = aor.endswith("αμην")
        astem = aor[:-4] if aor_middle else aor[:-1]
    else:
        aor_middle = middle_only
        astem = augment(stem)
    bare = unaugment(astem, stem) if aor else stem

    def person(tense, base, endings):
        for p, x in zip(PERSONS, endings):
            if doric:
                x = DORIC_1PL.get(x, x)
                if p == "3PL" and x == "ουσι":
                    x = "οντι"
            out.append((f"{tense}.{p}", base + x))

    if not middle_only:
        person("PRES", stem, PRESENT)
        out += [("INF", stem + "ειν"), ("IMP.SG", stem + "ε"), ("IMP.PL", stem + "ετε")]
        out += [(f"PTCP.PRES {t}", f) for t, f in adjective(stem + "οντος", stem + "οντον", False)]
    person("MID.PRES", stem, MID_PRESENT)
    out += [("MID.INF", stem + "εσθαι"), ("MID.IMP.SG", stem + "εσο"), ("MID.IMP.PL", stem + "εσθε")]
    out += [(f"PTCP.MID.PRES {t}", f) for t, f in adjective(stem + "ομενος", stem + "ομενον", False)]
    if not aor_middle:
        person("AOR", astem, AORIST)
        out += [(f"PTCP.AOR {t}", f) for t, f in adjective(bare + "αντος", bare + "αντον", False)]
    if aor_middle or not middle_only:
        person("MID.AOR", astem, MID_AORIST)
        out += [(f"PTCP.MID.AOR {t}", f) for t, f in adjective(bare + "αμενος", bare + "αμενον", False)]
    return [(t, final_sigma(f)) for t, f in out]


def paradigm(e):
    """[(tag, form)] for any entry; invariant words give just their headword(s)."""
    pos, g = e["pos"], e["greek"]
    if pos == "noun" and e.get("stem") not in (None, "irregular"):
        if first(g) in SPECIAL:
            return SPECIAL[first(g)]
        return decline(first(g), noun_class(e), construct=noun_class(e) in CONSTRUCT)
    if pos == "verb":
        return conjugate(e)
    if pos == "adj":
        an, inan = g.split(" / ")
        forms = adjective(an, inan)
        stem = inan[:-2]
        for degree, suffix in (("COMP", "οτερ"), ("SUPL", "οτατ")):
            forms += [(f"{degree} {t}", f) for t, f in adjective(stem + suffix + "ος", stem + suffix + "ον", False)]
        return forms
    if (pos == "num" or pos == "pron") and first(g).endswith("ος"):
        return decline(first(g), "O")  # ενος "one, someone", αλαφος "thousand"
    if first(g) == "αλληλιμ":
        return [(t, f) for t, f in decline("αλληλος", "O", False) if t.endswith("PL")]
    return [("", w.strip("-")) for w in words(g)]


def load_names():
    """Proper names: name, class (O, A, ON, adj or quoted), meaning."""
    names = []
    if not os.path.exists(NAMES):
        return names
    with open(NAMES, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.startswith(("#", "name\t")) or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) != 3:
                sys.exit(f"{NAMES}:{n}: expected 3 columns")
            names.append({"greek": cols[0], "kind": cols[1], "meaning": cols[2], "_line": n})
    return names


def name_paradigm(nm):
    g, kind = nm["greek"].lower(), nm["kind"]
    if kind == "adj":
        return adjective(g, g[:-2] + "ον")
    if kind == "quoted":
        return [("", g)]
    return decline(g, kind)


def nominal(tag):
    """Whether a form can take a possessive enclitic: a noun, adjective or participle form."""
    return bool(tag) and tag.split()[-1].split(".")[0] in CASES + ["AN", "IN", "CONSTR"]


def chant_forms(e):
    """[(tag, form)] built on the chant form, so chant texts can be checked. The lexicon
    gives a verb's chant infinitive but not its chant aorist, so verbs get no aorist forms."""
    if "chant" not in e or e["pos"] == "adj" and " / " not in e["chant"]:
        return []
    variant = {k: v for k, v in e.items() if k != "aorist"}
    variant["greek"] = e["chant"]
    return [(t, f) for t, f in paradigm(variant) if e["pos"] != "verb" or "AOR" not in t]


class Index:
    """Every inflected form of the lexicon and the names, for analysis."""

    def __init__(self, entries=None, names=None):
        self.forms = {}
        for e in entries if entries is not None else parse(DATA):
            for tag, form in paradigm(e) + chant_forms(e):
                self.add(form, (head(e), tag))
        for nm in names if names is not None else load_names():
            for tag, form in name_paradigm(nm):
                self.add(form, (nm["greek"], tag))

    def add(self, form, analysis):
        self.forms.setdefault(medial_sigma(form.lower()), []).append(analysis)

    def lookup(self, word):
        """Analyses of one word without hyphens, allowing a possessive enclitic."""
        w = medial_sigma(word.lower())
        found = list(self.forms.get(w, []))
        for enc in POSSESSIVE:
            if w.endswith(enc) and len(w) > len(enc) + 1:
                found += [(lemma, f"{tag} +{enc}") for lemma, tag in self.forms.get(w[:-len(enc)], [])
                          if nominal(tag)]
        return found

    def analyze(self, token):
        """Analyses of a written token such as ϸε-εσι-υ or ναϝᾱι; [] if unknown."""
        parts = [p for p in token.split("-") if p]
        while len(parts) > 1 and parts[0].lower() in PREFIXES:
            parts = parts[1:]
        while len(parts) > 1 and parts[-1].lower() in OBJECT:
            parts = parts[:-1]
        if len(parts) != 1:
            return []
        return self.lookup(parts[0])


# ---------------------------------------------------------------- tables

def cell(form, layer, bold=False):
    r = romanize({"greek": form, "layer": layer})
    star = "***" if bold else "*"
    return f"{star}{form}{star}<br>{r}"


def table_noun(e, cases=CASES):
    forms = dict(paradigm(e))
    lines = ["| Case | Singular | Dual | Plural |", "|------|----------|------|--------|"]
    for c in cases:
        row = " | ".join(cell(forms[f"{c}.{n}"], e["layer"]) for n in NUMBERS)
        lines.append(f"| **{c}** | {row} |")
    return lines


def table_eus(e):
    forms = dict(paradigm(e))
    lines = ["| Case | Singular |", "|------|----------|"]
    lines += [f"| **{c}** | {cell(forms[c + '.SG'], e['layer'])} |" for c in CASES]
    return lines


def table_adjective(e):
    forms = dict(paradigm(e))
    cols = [("AN", "SG"), ("IN", "SG"), ("AN", "DU"), ("AN", "PL"), ("IN", "PL")]
    lines = ["| Case | Animate SG | Inanimate SG | Animate DU | Animate PL | Inanimate PL |",
             "|------|-----------|--------------|------------|------------|--------------|"]
    for c in CASES:
        row = " | ".join(cell(forms[f"{g}.{c}.{n}"], e["layer"]) for g, n in cols)
        lines.append(f"| **{c}** | {row} |")
    return lines


def table_verb(e, tense):
    forms = dict(paradigm(e))
    lines = ["| | Singular | Dual | Plural |", "|--|----------|------|--------|"]
    for p, label in (("1", "1st"), ("2", "2nd"), ("3", "3rd")):
        sg, pl = forms[f"{tense}.{p}SG"], forms[f"{tense}.{p}PL"]
        lines.append(f"| {label} | {cell(sg, e['layer'])} | {cell(forms[f'{tense}.DU'], e['layer'])} | "
                     f"{cell(pl, e['layer'])} |")
    return lines


def table_doric_verb(e):
    forms = dict(paradigm(e))
    lines = ["| | Present | Aorist |", "|--|---------|--------|"]
    for p, label in zip(PERSONS, ("1sg", "2sg", "3sg", "dual", "1pl", "2pl", "3pl")):
        pres, aor = forms[f"PRES.{p}"], forms[f"AOR.{p}"]
        # the Doric endings are shown in bold
        lines.append(f"| {label} | {cell(pres, e['layer'], pres.endswith(('μες', 'ντι')))} | "
                     f"{cell(aor, e['layer'], aor.endswith(('μες', 'ντι')))} |")
    return lines


TABLES = {
    "noun": table_noun,
    "eus": table_eus,
    "adjective": table_adjective,
    "present": lambda e: table_verb(e, "PRES"),
    "aorist": lambda e: table_verb(e, "AOR"),
    "middle-present": lambda e: table_verb(e, "MID.PRES"),
    "middle-aorist": lambda e: table_verb(e, "MID.AOR"),
    "doric-verb": table_doric_verb,
}
MARKER = re.compile(r"<!-- inflect: (\S+) (\S+) -->\n(.*?)<!-- /inflect -->", re.S)


def render_tables(text, by_head):
    def repl(m):
        kind, word = m.group(1), m.group(2)
        if kind not in TABLES:
            sys.exit(f"unknown table kind {kind}")
        if word not in by_head:
            sys.exit(f"{word} is not in the lexicon")
        body = "\n".join(TABLES[kind](by_head[word]))
        # blank lines around the table keep the markers out of it in every Markdown renderer
        return f"<!-- inflect: {kind} {word} -->\n\n{body}\n\n<!-- /inflect -->"
    return MARKER.sub(repl, text)


def tables(check):
    by_head = {head(e): e for e in parse(DATA)}
    stale = []
    for name in sorted(os.listdir(DOCS)):
        path = os.path.join(DOCS, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if "<!-- inflect:" not in text:
            continue
        new = render_tables(text, by_head)
        if new == text:
            continue
        if check:
            stale.append(os.path.relpath(path))
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"wrote {os.path.relpath(path)}")
    if stale:
        sys.exit("out of date; run python3 tools/inflect.py --tables:\n  " + "\n  ".join(stale))
    if check:
        print("paradigm tables are up to date")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] in ("--tables", "--check"):
        tables(args[0] == "--check")
        return
    if args[0] == "--parse":
        index = Index()
        for w in args[1:]:
            found = index.analyze(w)
            print(f"{w}: " + ("; ".join(f"{lemma} {tag}".strip() for lemma, tag in found) or "unknown"))
        return
    by_head = {}
    for e in parse(DATA):
        by_head.setdefault(head(e), []).append(e)
    for w in args:
        if w not in by_head:
            print(f"{w}: not in the lexicon")
            continue
        for e in by_head[w]:
            print(f"{e['greek']} ({e['pos']}): {e['meaning']}")
            for tag, form in paradigm(e):
                print(f"  {tag:28} {form}")


if __name__ == "__main__":
    main()
