# Tharaic — A Fictional Language for a Seafaring Culture

## Cultural & Linguistic Context

**Who are the speakers?**
A seafaring people — traders, navigators, coastal settlers — living in a Mediterranean-analog world. They are pragmatic and poetic in equal measure: their oral tradition lives in sailor chants, navigation mnemonics, and oral contracts sealed with formulaic speech. Their written tradition covers trade ledgers, sea charts, and temple inscriptions.

**Linguistic ancestry:**
Tharaic descends from a proto-language that absorbed two streams:
- A **Greek-analog branch** → contributed vowel richness, inflectional endings, and poetic vocabulary
- A **Phoenician-analog branch** → contributed VSO word order tendency, trade/mercantile vocabulary, and some consonantal texture

Later, **literary Doric** (a second Greek-analog dialect, the language of poetry and learning) gave Tharaic a **high register**, much as French and Latin did for English: *χαδαρον* "room" next to *θαλαμος* "chamber".

---

## Contents

| Document | Covers |
|----------|--------|
| [Phonology & Script](docs/phonology.md) | Greek alphabet and extra letters, vowels, consonants, phonotactics, stress |
| [The Stele Typeface](docs/font.md) | An inscriptional font of straight, chiselled cuts for the alphabet, its extra letters and the romanization: design, use and specimen |
| [Morphology](docs/morphology.md) | Root system, gender, noun paradigms, construct state, pronouns, verbs (incl. "to be", imperfective past, middle voice), adjectives and comparison |
| [Syntax & Function Words](docs/syntax.md) | Word order, negation, questions, relative clauses, conditions, comparison, prepositions and their cases, conjunctions |
| [Registers](docs/registers.md) | Everyday and high speech, the learned Doric layer, doublets, pronunciation and grammar of the high register |
| [Dialects](docs/dialects.md) | Coastal standard, the conservative island dialect, and the harbor pidgin |
| [Word Building](docs/word-building.md) | Root patterns (older layer) and suffixes (younger layer) |
| [Lexicon](docs/lexicon.md) | About 1,450 words by theme, with roots, origins, chant forms and registers (generated from `data/lexicon.yaml`) |
| [Sample Sentences](docs/texts.md) | Glossed example sentences |
| [Proverbs & Oaths](docs/proverbs.md) | Sailor and merchant sayings, weather lore, oath formulas |
| [The Sacred Register](docs/sacred.md) | Temple speech: divine epithets, prayers, blessings, a votive inscription |
| [Chants & Stories](docs/stories.md) | A rowing chant and a glossed harbor tale |
| [Calendar & Star Lore](docs/calendar.md) | The star-set solar year, months, week, festivals, time of day, constellations |
| [Translating the Gospels](docs/gospels.md) | How Greek constructions, titles and names are rendered; the Lord's Prayer and John 1:1 |
| [Mark 1](docs/mark-1.md) | The first chapter of Mark in the high register: running text, then verse by verse with gloss and notes |
| [History](docs/history.md) | Sound changes from Proto-Tharaic, root vowel grades, chant forms, irregular nouns |
| [Roadmap](docs/roadmap.md) | Planned work |

## Tools

Python 3 scripts, standard library only except the font builder:

- `python3 tools/greek.py nāvei navos` — convert romanized Tharaic to Greek script, or back with `--roman` (reads stdin if no words are given)
- `python3 tools/check_phonotactics.py [files…]` — list words in the docs that break the everyday syllable rules, the strict chant rules with `--chant`, or the high-register rules with `--high` (defaults to `docs/*.md`)
- `python3 tools/dialect.py "…"` — turn coastal Tharaic into the island dialect (chant forms, construct vowel, *ϸ* → *σ*)
- `python3 tools/build_lexicon.py` — check every entry in `data/lexicon.yaml` (grammar fields, romanization, syllable rules, chant forms, sound changes) and regenerate `docs/lexicon.md`; `--check` only verifies it is up to date. It also checks that every word in `data/gospels.tsv` is in the lexicon
- `python3 tools/build_font.py` — build the [Stele typeface](docs/font.md) into `font/` and its specimen; needs `pip install fonttools skia-pathops brotli`

---

## Architecture Summary

```
THARAIC
│
├── PHONOLOGICAL LAYER
│   └── Open syllable, max CVC, no clusters (strict in chant;
│       everyday speech allows obstruent + ρ/λ)
│       ├── New: ϸ /ʃ/
│       ├── New: ϙ /ɣ/
│       └── High register: Doric clusters kept (ψ, κτ, στρ)
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
├── VERBAL LAYER
│   ├── Inflection: Greek (person/number/tense)
│   ├── Voice: active / middle (Greek -ομαι)
│   ├── "To be": present ε(σ)- (Greek) + past/future Κ-Ν (Phoenician)
│   ├── Future: particle ϸα (Phoenician-analog)
│   ├── Imperfective past: εκανα + present (Hebrew hāyāh-analog)
│   ├── Participles: adjectives in -οντος (present), -αντος (aorist)
│   └── Narrative past: ϝα- prefix (Phoenician wayyiqtol-analog)
│
├── CLAUSE LAYER
│   ├── Negation: βαλ (Phoenician) for facts, μη (Greek) for commands/wishes/conditions
│   ├── Wishes: λυ (Phoenician-analog) + present
│   ├── Questions: ͱα- prefix (Phoenician); fronted question words
│   ├── Relative clauses: ϸε- + resumptive pronoun (Phoenician)
│   └── Conditions: ιμ "if" (Phoenician) + αν "would" (Greek)
│
├── WORD-BUILDING LAYER
│   ├── Older: vowel patterns on roots, μα- places, -υτον abstracts (Phoenician)
│   └── Younger: -ικος, -ιον, -ευς suffixes (Greek)
│
├── DIALECT LAYER
│   ├── Coastal: the standard
│   ├── Island: no changes 2–3 (τιρια, ναϝιτα), ϸ merged with σ
│   └── Harbor pidgin: SVO, no case endings, tense particles
│
└── REGISTER LAYER
    ├── Everyday: native, Phoenician and sailors' Greek words
    └── High: learned Doric words (ᾱ for η, clusters), aorist narration,
        genitive over construct, participles; includes temple speech
```
