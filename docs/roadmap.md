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
4. **Lexicon** — `data/lexicon.yaml` with about 300 entries, generated into `docs/lexicon.md`. Four themes: body & kinship, weather & sea life, trade & craft, ritual & abstract. Each entry records Greek spelling, romanization, root, part of speech, gender and stem class, meaning, source layer (native, Phoenician, Greek), and the chant form where it differs.

## Later

| Future phase | What it adds |
|---|---|
| **Proverb collection** | Fixed expressions, sailor sayings, trade oaths |
| **Sacred/religious register** | Temple language, divine epithets, ritual formulas |
| **Texts & culture** | Chants, a calendar and star lore, a glossed story |
| **Script details** | Punctuation, Greek-style alphabetic numerals |
| **Dialectal variation** | Coastal dialect vs. island dialect vs. trade pidgin |
