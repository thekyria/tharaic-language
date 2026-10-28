# Dialects

[← Overview](../README.md)

The [registers](registers.md) are vertical variation: who you are and what the occasion is. Dialects are horizontal: where you are from. Tharaic has three main varieties, and they are mutually intelligible. Each one comes from the [history](history.md) of the language: which sound changes reached it, and what it was in contact with.

| Variety | Spoken by | Main features |
|---------|-----------|---------------|
| **Coastal** | the harbor cities and the coast | the standard described in these docs; the base of the high register |
| **Island** | the islands | changes 2 and 3 never arrived, so everyday words have the chant forms; *ϸ* has merged with *σ*; a few words of its own |
| **Harbor pidgin** | Tharaic merchants and foreigners in the ports | no case endings, one verb form, SVO order, particles for tense |

---

## Coastal

The coastal dialect is the language described in the rest of these docs. It is the standard for two reasons. Changes 2–4 began in the harbor cities, and the Doric schools and the great temples stand there too. So the [high register](registers.md) is built on coastal speech, and educated islanders learn it as a second variety.

---

## Island

### Why it differs

Changes 2 and 3, the loss of short vowels before the stress and the loss of the construct's final vowel ([History § 2](history.md#2-sound-changes)), spread from the harbor cities along the coast. They never crossed the open sea. Islanders still say the older forms that the coast keeps only in [chant](history.md#3-the-chant-register). They also kept the strict syllable rules, so later loans with clusters are broken up in their mouths, as in chant.

To coastal ears, islanders "talk like a hymn": old-fashioned and pious, and a little comic. Islanders say the coast "swallows its vowels". Every coastal speaker knows the chant forms from songs and the temple, so the two dialects understand each other without effort.

### Sounds

| Feature | Coastal | Island | Rule |
|---------|---------|--------|------|
| Old short vowels | *τρια*, *προς*, *βραδυς*, *μιζραχᾱ* | *τιρια*, *πορος*, *βοραδυς*, *μιζιραχᾱ* | change 2 did not happen |
| Construct | *ναϝιτ μᾱλικος*, *λακυλ θᾱρος* | *ναϝιτα μᾱλικος*, *λακυλα θᾱρος* | change 3 did not happen |
| Loan clusters | *αστρος*, *ξενος*, *ψυχᾱ* | *αστορος*, *κεσενος*, *πυσυχᾱ* | a copy of the following vowel |
| *ϸ* /ʃ/ | *ϸαμον* "sky", *ϸα* (future) | *σαμον*, *σα* | **ϸ merged with σ**, an island innovation |

The merger of *ϸ* with *σ* is the one change of the islands' own. Islanders cannot say "sh", which the coast finds as telling as the *shibboleth* of Judges 12. It makes some words sound alike:

| Coastal | | Coastal | | Island, both |
|---------|--|---------|--|--------------|
| *ϸαμον* | sky | *σαμον* | thirst | *σαμον* |
| *ναϸον* | debt | *νασον* | temptation | *νασον* |
| *ϸελεχειν* | to send | *σελεχειν* | to forgive | *σελεχειν* |
| *ρεϸειν* | to begin | *ρεσειν* | to run | *ρεσειν* |
| *ϸακαλον* | shekel | *σακαλον* | understanding | *σακαλον* |
| *ϸεκερειν* | to lie, deceive | *σεκερειν* | to hire | *σεκερειν* |

Coastal sailors joke that in the Lord's Prayer, *Σελεχε ναϸαεν… Και μη νεͱεγε-νεν προς νασον.* "Forgive our debts… and do not lead us into temptation", islanders ask to be forgiven their temptations and kept out of debt.

`tools/dialect.py` applies these rules to any coastal text, using the chant forms in the lexicon.

### Grammar

- **The narrative past *ϝα-*** is the normal way to tell the past, in writing too: island chronicles and letters use it.
- **The construct** is still used freely for what belongs to someone by nature, such as kin and the parts of the body: island *ϳαδυλα ναϝος* "the sailor's hand", coastal *ϳαδον ναϝι*.
- **The high register** reaches the islands late. An island priest's formal speech is the older temple style, with Phoenician words and *ϝα-*. When islanders use a Doric word, they break its clusters: *σοχολᾱ* "school".

### Words

A few words are used only on the islands. They are marked *island* in the [lexicon](lexicon.md):

| Island | Coastal | Meaning |
|--------|---------|---------|
| *μαλαχος* | *ναϝος* | sailor, "the salt-man" (cf. Hebrew *mallāḥ*) |
| *νᾱϝος* | — | voyager, one who is always at sea: the old actor noun behind *νᾱϝειν*, lost on the coast |
| *ιϳον* | *νησον* | island; one's home island (Phoenician *ʾy*) |
| *σαφονος* | — | the north wind (Phoenician *ṣpn*) |
| *ϙαραβος* | — | the west wind, the evening wind (Phoenician *ʿrb*) |
| *ϳαραχᾱ* | *σεληνᾱ* | the moon. On the coast, *ϳαραχᾱ* lives only in old sacred formulas |

---

## Harbor pidgin

### Who speaks it

In the ports, Tharaic merchants trade with sailors from many coasts who never learn Tharaic properly. Between them they use a reduced Tharaic: a pidgin, nobody's mother tongue. Every Tharaic merchant can speak it, and coastal speakers understand it without being taught, though they find it rough.

### Grammar

| Feature | Coastal | Pidgin |
|---------|---------|--------|
| Word order | VSO: *Νᾱϝει ναϝος ναϝᾱν.* | **SVO**: *Ναϝος νᾱϝει ναϝᾱ.* "The sailor sails the ship." |
| Nouns | eight cases, three numbers | one form, the nominative singular; *πολυ* "many" or a number marks the plural: *πολυ ναϝος* "sailors", *δεχα ϸακαλον* "ten shekels" |
| The sea cases | *λιμελι*, *ναϝαθα*, *φιλομ* | prepositions: *εν λιμᾱ* "in the harbor", *απο ναϝᾱ* "from the ship", *συν φιλος* "with a friend" |
| Indirect object | dative: *λεκει ναϝοι* | *δωε* "to, for", from the imperative "give!": *λεκει δωε ναϝος* |
| Possession | genitive or construct | the owner after the thing, with no ending: *βᾱσιλος ναϝᾱ* "the ship's captain" |
| Adjectives | before the noun, agreeing | after the noun, unchanged: *ϳαινον καλον* "good wine" |
| Pronouns | with enclitics, animate and inanimate | only the independent ones: *ανι, ατα, ͱῡα, ανεν, ατεμ, ͱῡιμ*; *ͱῡα* for "he, she, it" |
| Verbs | person, tense, voice | one form, the 3rd singular present: *ανι ϝενει* "I come", *ͱῡιμ ϝενει* "they come"; also the command: *Ϝενει!* "Come!" |
| Tense | aorist, *ϝα-*, *ϸα* | particles before the verb: past *κεβαρ* "already", future *ϸα* |
| Negation | *βαλ*, *μη* | only *βαλ*, before the verb |
| "To be" | a full verb | *εσι* for all persons, often left out: *Ζε ϳαινον καλον.* "This wine is good." |
| Questions | *ͱα-*, question words first | rising voice; question words first: *Ποσον…?* "How much…?" |

The pidgin keeps the coastal spelling of its words, though foreign speakers often drop vowel length and break clusters.

### At the market

A foreign trader (A) and a Tharaic wine merchant (B):

> **A:** *Ποσον ζε ϳαινον?*<br>
> Poson ze yainon?<br>
> How-much this wine?<br>
> “How much is this wine?”

> **B:** *Ζε ϳαινον καλον πολυ. Δεχα ϸακαλον.*<br>
> Ze yainon kalon polu. Dekha shakalon.<br>
> This wine good very. Ten shekel.<br>
> “This wine is very good. Ten shekels.”

> **A:** *Βαλ! Ανι δωει πεντε.*<br>
> Bal! Ani dōei pente.<br>
> No! I give five.<br>
> “No! I'll give five.”

> **B:** *Επτα. Ανι δωει πολυ ϳαινον δωε ατα.*<br>
> Epta. Ani dōei polu yainon dōe ata.<br>
> Seven. I give much wine to you.<br>
> “Seven, and I'll give you plenty of wine.”

> **A:** *Ναι. Ανι κεβαρ φερει κασαφον απο ναϝᾱ.*<br>
> Nai. Ani kebar pherei kasaphon apo navā.<br>
> Yes. I PAST bring silver from ship.<br>
> “All right. I've brought silver from the ship.”

> **B:** *Καλον! Ατα ϸα ϝενει μαχαρ?*<br>
> Kalon! Ata sha venei makhar?<br>
> Good! You FUT come tomorrow?<br>
> “Good! Will you come back tomorrow?”

In coastal Tharaic, the trader's last line would be *Ναι. Εφερα κασαφον εκ ναϝαθα.*

---

## The same passage in three dialects

> **Coastal:** *Ϝα-ιδει βᾱσιλ ναϝᾱ σᾱϙιρον, ϝα-ͱεφεκει ναϝᾱν προς λιμᾱν, ϝα-λεκει ναϝοιμ: «Βαλ ϸα νᾱϝομεν ͱαϳομ: τρια ͱημερα ϸα κανει σᾱϙιρος.»*<br>
> Va-idei bāsil navā sāghiron, va-hephekei navān pros limān, va-lekei navoim: «Bal sha nāvomen hayom: tria hēmera sha kanei sāghiros.»

> **Island:** *Ϝα-ιδει βᾱσιλα ναϝᾱ σᾱϙιρον, ϝα-ͱεφεκει ναϝᾱν πορος λιμᾱν, ϝα-λεκει μαλαχοιμ: «Βαλ σα νᾱϝομεν ͱαϳομ: τιρια ͱημερα σα κανει σᾱϙιρος.»*<br>
> Va-idei bāsila navā sāghiron, va-hephekei navān poros limān, va-lekei malakhoim: «Bal sa nāvomen hayom: tiria hēmera sa kanei sāghiros.»

> **Pidgin:** *Βᾱσιλος ναϝᾱ κεβαρ ιδει σᾱϙιρος. Ͱῡα ͱεφεκει ναϝᾱ προς λιμᾱ. Ͱῡα λεκει δωε πολυ ναϝος: «Ανεν βαλ νᾱϝει ͱαϳομ. Σᾱϙιρος ϸα εσι τρια ͱημερον.»*<br>
> Bāsilos navā kebar idei sāghiros. Hūa hephekei navā pros limā. Hūa lekei dōe polu navos: «Anen bal nāvei hayom. Sāghiros sha esi tria hēmeron.»

"The ship's captain saw the storm, turned the ship toward the harbor, and said to the sailors: 'We will not sail today: the storm will last three days.'"

The island version is the coastal one passed through `tools/dialect.py`: *βᾱσιλα* (construct), *πορος*, *σα*, *τιρια*, with the island word *μαλαχοιμ* "sailors". The pidgin changes the grammar instead: SVO order, *κεβαρ* for the past, *δωε πολυ ναϝος* "to the sailors", and nouns that do not change (*ναϝᾱ*, *λιμᾱ*, *τρια ͱημερον*).
