# Roadmap

[← Overview](../README.md)

## Design decisions

| Topic | Decision |
|-------|----------|
| Overall feel | **Naturalistic**: irregular forms are allowed when a documented sound change explains them |
| Consonant clusters | Explained **by history** ([History](history.md)): Proto-Tharaic had no clusters; everyday speech later lost short vowels before the stress next to ρ/λ, and later loans kept clusters of the same shape. Chant keeps the older forms of native words (*τιρια*) and breaks up loan clusters with an echo vowel (*αστορος*) |
| Word building | **Two layers**: older Phoenician-style vowel patterns on roots (agent CeC-ος, result CaC-ον, place/instrument μα-CaC-αρ) plus younger Greek-style suffixes (-ικος, diminutive -ιον, tradesman -ευς) |
| Negation | Two particles: **βαλ** for statements (Phoenician *bl*), **μη** for commands and wishes (Greek *μή*) |
| "To be" | A full verb in every tense, built from two roots: a Greek-like present (*εμι, εις, εσι…*) and Phoenician Κ-Ν for past and future (*εκανα* "I was", *ϸα κανω* "I will be") |
| Noun dual | **-ιν** becomes the general dual marker: *θᾱριν*, *ναϝιν*, *καλιν*; INS dual -ομεν → **-ομιν**. This frees -ειν for infinitives only |
| Registers | **Two tiers**: everyday and high. The high register draws on **literary Doric**, whose prestige comes from poetry and learning. The older Greek-analog loans are re-read as **sailors' Greek** (Ionic-analog, with *η*), so the two layers give same-word doublets (*ͱημερον* / *ͱᾱμερᾱ*). Temple speech becomes a style of the high register, with Doric theology words; Phoenician words survive in formulas and divine names. The high register keeps Doric clusters, prefers the aorist, the genitive and participles, and keeps some Doric endings. Scripture is in the high register |
| Dialects | **Three mutually intelligible varieties**, each explained by history: the coastal standard; the island dialect, which never had changes 2–3 (its everyday words are the coastal chant forms) and merged *ϸ* with *σ*; and an SVO harbor pidgin without case endings. No creole; places stay unnamed |
| Typeface | **Inscriptional**: one alphabet of capitals in even, straight chisel cuts (round letters on a diamond, C as ⟨) with wedge-flared heads (as in Wedge) and archaic letterforms (pointed bowls, ⊕, ⌶, short-legged Π, diamond Ο Θ Φ Ϙ Ω), lowercase as small capitals, Latin letters for the romanization, with U written V; built from code in `tools/build_font.py`, with the font files in `font/` |
| Repository | Overview in `README.md`, content in `docs/`, dictionary data in `data/lexicon.yaml`, scripts in `tools/` |

## Plan

Each step is a separate pull request.

1. ✅ **Restructure** — split the README into `docs/`, add the Greek conversion and phonotactics-check tools. No content changes.
2. ✅ **History & consistency fixes** — new `docs/history.md` with the sound changes from Proto-Tharaic, and fixes that follow from it:
   - the cluster story (above) for words like *αστρος*, *τρια*, *προς*, *επτα*, *μιζραχᾱ*
   - θ/τ in root Τ-Ρ: τ became θ before a stressed long vowel (\*τᾱρος → *θᾱρος*, but *ταρον*)
   - ε/α alternation inside roots (*λεκ-* for verbs and agents, *λακ-* for results)
   - gender leftovers such as *ͱυδᾱ*, *ρεμα*, *αστρα*
   - the dual change to -ιν
   - the A-stem construct ending *-ιτ*, whose final τ breaks the coda rule
   - corrected sample sentences: the *-ειμ* ending, *καπανοι* → *καπανιμ*, the "crew" gloss, narrative ϝα- with present vs aorist, the case after *επι*
3. ✅ **Grammar** — negation, yes/no questions with ͱα-, question words, relative clauses with ϸε-, conditionals (if/when/unless), the case each preposition takes, "to be", the two layers of word building, imperfective past, middle voice, comparatives.
4. ✅ **Lexicon** — `data/lexicon.yaml` with about 400 entries (planned as about 300), generated into `docs/lexicon.md`. Four themes: body & kinship, weather & sea life, trade & craft, ritual & abstract. Each entry records Greek spelling, romanization, root, part of speech, gender and stem class, meaning, source layer (native, Phoenician, Greek), and the chant form where it differs.

5. ✅ **Texts** — [Proverbs & Oaths](proverbs.md), [the Sacred Register](sacred.md), and [Chants & Stories](stories.md) (a rowing chant and a glossed tale). The texts added the grammar they needed: the wish particle *λυ*, adjective position, long subjects moving last, *ενος ϸε-* "he who", the demonstrative *ζε*, and case marking at the end of a construct phrase. Their new words are in the lexicon.

6. ✅ **Calendar & star lore** — [Calendar & Star Lore](calendar.md): a solar year set by the rising and setting of the Doves (the Pleiades), split into the Open Sea and the Closed Sea; twelve 30-day months and the Days of Memory; a seven-day planetary week; year counting by judges and from the Voyage of the Beginning; the night watches; festivals; constellations and navigation stars. Adds number labels after a noun (*ͱημερον τρια* "day three") and a *Time, Calendar & Stars* section of the lexicon.

7. ✅ **Gospel vocabulary** — about 710 new words, so that every word of the four Gospels (about 2,690 Greek dictionary forms besides names, checked one by one against the SBL Greek New Testament) has a Tharaic equivalent or a regular construction. Five new lexicon sections (*Land, Plants & Animals*; *House, Food & Clothing*; *City, Law & Power*; *Mind, Speech & Feeling*; *Movement & Position*). Most new words are native, built on roots with Hebrew cognates; Roman and Greek things (the denarius, the praetorium) are Greek-layer loans. [Translating the Gospels](gospels.md) gives the constructions, rules for names, and two sample passages. The grammar gained adverbs from adjectives, *παϙαμα* "times", *βιλτι* "without", the reflexive with *νεφεϸᾱ*, the middle imperative, new prepositions and conjunctions, and the CiCeC-ος pattern for bodily defects.

8. ✅ **Mark 1** — [the first chapter of Mark](mark-1.md), in narrative prose with the *ϝα-* past (rewritten in the high register in step 12), as running text and verse by verse. Running text needed a few additions: *ϝα-* in written sacred narrative, *ϝα-κανει* "and it came to pass", object enclitics after prepositions and as indirect objects (*προς-υ*, *λεκει-υ*, *εσι-υ* "he has"), *απο* + enclitic in comparisons, agreement with compound subjects, *λυ* "let us", and the noun *ταͱαρον* "cleansing".

9. ✅ **Registers: design** — [Registers](registers.md): the two registers, the two Greek streams, kinds of doublet, high-register pronunciation (ᾱ for η, kept clusters, hyperdorism, chant forms) and the planned grammar. The Doric city and the registers stay unnamed in-world. The lexicon gains the `doric` layer and the `register` and `doublet` fields, checked by `tools/build_lexicon.py`; `tools/check_phonotactics.py` gains `--high`. Ten example entries.

10. ✅ **Registers: vocabulary** — about 280 new Doric words, so the lexicon has about 290 high-register words, about 180 of them in doublets. They cover poetry and music, philosophy and mathematics, schooling, virtues and feelings, theology, law and war, medicine, polite speech, and poetic words for nature. A new lexicon section, *Learning, Arts & Science*. About 55 learned adjectives for everyday nouns (*σεληνᾱ* / *σελᾱναιος*, like English *moon* / *lunar*), with a `base` field. Three Doric noun classes (-ᾱς, -μα, -ις). *ηλος* stays the name of God; the high register adds only the adjective *θειος* "divine".

11. ✅ **Registers: grammar** — [Doric nouns](morphology.md#doric-nouns-high-register): Doric endings in the five Greek cases, Tharaic endings in the sea cases and the dual. [Doric verbs](morphology.md#doric-verbs-high-register): 1st plural *-μες*, 3rd plural *-ντι*, and the Greek aorist stem, now recorded in the lexicon for every Doric verb. [Participles](morphology.md#participles) as regular adjectives (*νᾱϝοντος*, *νᾱϝαντος*, *φερομενος*, *φεραμενος*), replacing the old *νᾱϝον* / *νᾱϝουσα*. [Participle phrases](syntax.md#participle-phrases) and the genitive absolute; Doric conjunctions (*αι*, *ͱοκα*, *ͱινα*, *γαρ*…) for [high-register clauses](syntax.md#high-register-clauses). *ϝα-* becomes the past of oral tales; the construct is kept only in divine names and fixed titles. [The Sacred Register](sacred.md) is now a style of the high register: old formulas kept word for word, new high-style hymns, prayers and inscriptions.

12. ✅ **Registers: scripture** — [Mark 1](mark-1.md) rewritten in the high register: aorist narration, participle phrases, genitive absolutes, Doric words with Doric endings, *αι*, *ͱοκα*, *ͱινα*, *γαρ*, *ωστε* + infinitive. The Gospel titles (*μαλκυλ ηλος*, *βενιλ αδαμος*, *καδοϸος ρῡχᾱ*) are fixed and keep the construct and their native words. `data/gospels.tsv` now gives the Doric word wherever one exists for the same Greek word (about 170 rows), and `tools/build_lexicon.py` refuses everyday-only words there. [Translating the Gospels](gospels.md): high-register constructions, the Lord's Prayer in both registers, John 1:1 with *λογος*.

13. ✅ **Dialects** — [Dialects](dialects.md): the coastal standard, the island dialect (sound rules, the *ϸ*/*σ* homophones, grammar, island words) and the harbor pidgin (grammar table, a market dialogue), with one passage in all three. `tools/dialect.py` turns coastal text into island forms; the lexicon gains a `dialect` field, five island words and two pidgin words.

14. ✅ **Typeface** — [The Stele Typeface](font.md): an inscriptional font covering the whole alphabet with its extra letters (*Ϝ Ͱ Ϳ Ϸ Ϙ*, *ᾱ ῡ*), straight chisel cuts with diamond-based round letters, stroke heads flared like wedges, archaic letterforms, Latin letters and long vowels for the romanization, lowercase drawn as small capitals, digits and the punctuation the docs use, basic kerning and macron placement. `tools/build_font.py` draws each letter as a stroked skeleton and writes `font/TharaicStele.ttf`, `.woff2` and the specimen.

15. ✅ **Wedge typeface** — [Tharaic Wedge](font.md#tharaic-wedge): a second face drawing the same letters as cuneiform wedges pressed into clay, for tablets and ledgers, with at most four wedges per letter (triangle-based Θ Φ Ϙ Ω, a Phoenician-style Β, simpler S, digits and ?). `tools/build_font.py` builds both faces from the same skeletons.

## Later

| Future phase | What it adds |
|---|---|
| **Script details** | Punctuation, Greek-style alphabetic numerals |
