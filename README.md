# Tharaic — A Fictional Language for a Seafaring Culture

## Cultural & Linguistic Context

**Who are the speakers?**
A seafaring people — traders, navigators, coastal settlers — living in a Mediterranean-analog world. They are pragmatic and poetic in equal measure: their oral tradition lives in sailor chants, navigation mnemonics, and oral contracts sealed with formulaic speech. Their written tradition covers trade ledgers, sea charts, and temple inscriptions.

**Linguistic ancestry:**
Tharaic descends from a proto-language that absorbed two streams:
- A **Greek-analog branch** → contributed vowel richness, inflectional endings, and poetic vocabulary
- A **Phoenician-analog branch** → contributed VSO word order tendency, trade/mercantile vocabulary, and some consonantal texture

---

## Contents

| Document | Covers |
|----------|--------|
| [Phonology & Script](docs/phonology.md) | Greek alphabet and extra letters, vowels, consonants, phonotactics, stress |
| [Morphology](docs/morphology.md) | Root system, gender, noun paradigms, construct state, pronouns, verbs, adjectives |
| [Syntax & Function Words](docs/syntax.md) | Word order, prepositions, conjunctions |
| [Lexicon](docs/lexicon.md) | Vocabulary by theme, numbers, core verbs and adjectives |
| [Sample Sentences](docs/texts.md) | Glossed example sentences |
| [History](docs/history.md) | Sound changes from Proto-Tharaic, root vowel grades, chant forms, irregular nouns |
| [Roadmap](docs/roadmap.md) | Planned work |

## Tools

Python 3 scripts, standard library only:

- `python3 tools/greek.py nāvei navos` — convert romanized Tharaic to Greek script (reads stdin if no words are given)
- `python3 tools/check_phonotactics.py [files…]` — list words in the docs that break the everyday syllable rules, or the strict chant rules with `--chant` (defaults to `docs/*.md`)

---

## Architecture Summary

```
THARAIC
│
├── PHONOLOGICAL LAYER
│   └── Open syllable, max CVC, no clusters (strict in chant;
│       everyday speech allows obstruent + ρ/λ)
│       ├── New: ϸ /ʃ/
│       └── New: ϙ /ɣ/
│
├── ROOT LAYER (Phoenician)
│   └── Bi/triconsonantal roots carry meaning
│       └── Vowels carry grammar
│
├── NOMINAL LAYER
│   ├── Gender: Animate / Inanimate
│   ├── Number: Singular / Dual / Plural
│   ├── Cases: 8 (NOM ACC GEN DAT VOC | LOC INS ABL)
│   │   └── "sea cases" are the Phoenician layer
│   └── Stems: O-stem / A-stem / ON-stem / AR-stem
│
├── POSSESSION LAYER
│   ├── Genitive (Greek) — everyday
│   └── Construct state (Phoenician) — titles, sacred
│
├── PRONOMINAL LAYER (Phoenician)
│   ├── Independent pronouns (ανι, ατα…)
│   └── Enclitics
│       ├── on verbs (-νι, -τα…)
│       └── on nouns (-ι, -κα…)
│
└── VERBAL LAYER
    ├── Inflection: Greek (person/number/tense)
    ├── Future: particle ϸα (Phoenician-analog)
    └── Narrative past: ϝα- prefix (Phoenician wayyiqtol-analog)
```
