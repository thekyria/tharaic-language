# Translating the Gospels

[← Overview](../README.md)

The [lexicon](lexicon.md) has enough words to translate the four Gospels. Every word of the Greek text, about 2,690 dictionary forms besides names, was checked against the lexicon (using the lemmas of the SBL Greek New Testament). Each one has a Tharaic word, or a regular construction from the grammar. The full list is [`data/gospels.tsv`](../data/gospels.tsv): Greek word, number of occurrences, Tharaic equivalent, and how it is rendered; `tools/build_lexicon.py` checks that every Tharaic word in it is in the lexicon. This page lists those constructions, gives rules for names, and ends with two sample passages. A whole chapter is translated in [Mark 1](mark-1.md).

---

## Greek constructions

| Greek | Tharaic | Example |
|-------|---------|---------|
| The article *ὁ, ἡ, τό* | not translated: Tharaic has no article | |
| Compound verbs (*εἰσ-*, *ἐξ-*, *ἀπ-*…) | a verb of its own for the common ones, otherwise the simple verb with a preposition or a [sea case](morphology.md#noun-paradigms) | *βεϝειν* "go in", *ϳεσειν* "go out", *ϙελειν* "go up", *ϳερεδειν* "go down", *ϸεβειν* "turn back" |
| Passive | the [middle voice](morphology.md#middle-voice), agent in the ablative | *κεδεϸεται* "is made holy" |
| *ἔχω* "have" | "to be" with the owner in the dative ([To be](morphology.md#to-be)); *εχεζειν* "hold" for physical holding | |
| Adverbs in *-ως* | the inanimate adjective ([Adverbs](syntax.md#adverbs)) | *καλον* "well" |
| *τρίς*, *ἑπτάκις* | number + *παϙαμα* | *τρια παϙαμα* "three times" |
| Ordinals | a number after the noun ([Calendar § Dates](calendar.md#dates)) | *ͱημερον τρια* "the third day" |
| Negative adjectives in *ἀ-* | *βιλτι* + ablative | *βιλτι αμαναθα* "unbelieving" |
| *ἑαυτοῦ* "himself" | *νεφεϸᾱ* + possessive ([Reflexive](morphology.md#reflexive-oneself)) | *νεφεϸᾱνκα* "yourself" |
| *ἀμὴν λέγω ὑμῖν* | *αμεν* first, as in the Greek | *Αμεν, λεκω-τεμ…* "Amen, I tell you…" |

**Titles** are construct phrases ([Construct state](morphology.md#construct-state--phoenician-possession)):

| Tharaic | Romanized | Meaning |
|---------|-----------|---------|
| *βενιλ αδαμος* | benil adamos | the Son of Man (cf. Hebrew *ben-ʾādām*) |
| *βενιλ ηλος* | benil ēlos | the Son of God |
| *μαλκυλ ηλος* | malkul ēlos | the kingdom of God |
| *μαλκυλ ϸαμον* | malkul shamon | the kingdom of heaven |
| *καβασιυλ ηλος* | kabasiul ēlos | the Lamb of God |
| *καδοϸος ρῡχᾱ* | kadoshos rūkhā | the Holy Spirit (an attributive adjective, not a construct) |
| *Μᾱϸιχος* | Māshikhos | the Christ, the Anointed |

---

## Names

1. **Source.** Hebrew and Aramaic names take their Semitic form, with the same letters as native roots: ʿ is *ϙ*, ḥ is *χ*, š is *ϸ*, ṣ is *σ*, y is *ϳ*, w is *ϝ*. Greek and Latin names (Pilate, Philip, Caesar) keep their Greek form.
2. **Syllables.** A cluster the [rules](phonology.md#phonotactics--the-no-cluster-rule) do not allow is broken by a copy of the following vowel, as in the [chant register](history.md#3-the-chant-register): *Bêt-Leḥem* → *Βητελεχεμον*. Double consonants are written single: *Φιλιπος*.
3. **Endings.** Men's names ending in -a take the A-stem *-ᾱ* (*Ϳεͱυδᾱ*); other men's names take the O-stem *-ος*, which replaces a final -o (*Ϸελομος*). Women's names take *-ᾱ*. Places are inanimate and take the ON-stem *-ον*.
4. **"Son of"**, Aramaic *bar*, is the construct *βενιλ*: *Ϸιμϙωνος βενιλ Ϳωνᾱ* "Simon son of Jonah".
5. **Peoples and languages** are adjectives in *-ικος*: *Ϳεͱυδικος* "Judean, a Jew", *λαϸανον ϙιβρικον* "the Hebrew language".

| Greek | Tharaic | Romanized | From |
|-------|---------|-----------|------|
| Ἰησοῦς | *Ϳεϸῡϙος* | Yeshūghos | *Yēšûaʿ*, root Ϳ-Ϸ-Ϙ "save", as in *ϳεϸεϙειν* |
| Ἰωάννης | *Ϳωχανανος* | Yōkhananos | *Yôḥānān* |
| Σίμων | *Ϸιμϙωνος* | Shimghōnos | *Šimʿôn* |
| Πέτρος, Κηφᾶς | *Κηφᾱ* | Kēphā | Aramaic *Kêpā* "rock" |
| Ἰάκωβος | *Ϳαϙακωβος* | Yaghakōbos | *Yaʿăqōb* |
| Ζεβεδαῖος | *Ζεβαδιᾱ* | Zebadiā | *Zəbadyāh* |
| Ἀνδρέας | *Ανδρεος* | Andreos | Greek |
| Φίλιππος | *Φιλιπος* | Philipos | Greek |
| Θωμᾶς | *Τωμᾱ* | Tōmā | Aramaic *Təʾômā* "twin" |
| Ἰούδας | *Ϳεͱυδᾱ* | Yehudā | *Yəhûdāh* |
| Μαρία, Μαριάμ | *Μιρϳαμᾱ* | Miryamā | *Miryām* |
| Μάρθα | *Μαρθᾱ* | Marthā | Aramaic *Mārtā* |
| Μαγδαληνή | *Μαγαδαλικος* | Magadalikos | of Magdala, *Μαγαδαλον* "tower" (cf. *μαγαδαλαρ*) |
| Ἰωσήφ | *Ϳωσεφος* | Yōsephos | *Yôsēp* |
| Λάζαρος | *Ελϙαζαρος* | Elghazaros | *ʾElʿāzār* |
| Δαυίδ | *Δαϝιδος* | Davidos | *Dāwīd* |
| Μωϋσῆς | *Μωϸεος* | Mōsheos | *Mōšeh* |
| Ἀβραάμ | *Αβραͱαμος* | Abrahamos | *ʾAbrāhām* |
| Ἰσαάκ | *Ϳισχακος* | Yiskhakos | *Yiṣḥāq* |
| Ἰσραήλ | *Ϳισραηλος* | Yisraēlos | *Yiśrāʾēl* |
| Ἠλίας | *Ηλιϳᾱ* | Ēliyā | *ʾĒlîyāh* |
| Ἠσαΐας | *Ϳεϸαϙιϳᾱ* | Yeshaghiyā | *Yəšaʿyāh* |
| Ἰωνᾶς | *Ϳωνᾱ* | Yōnā | *Yônāh*, the same word as *ϳωνᾱ* "dove" |
| Σολομών | *Ϸελομος* | Shelomos | *Šəlōmōh* |
| Γαβριήλ | *Γαβριηλος* | Gabriēlos | *Gabrîʾēl* |
| Ἐμμανουήλ | *Ϙιμανυηλος* | Ghimanuēlos | *ʿImmānû ʾēl* "God with us" |
| Βαραββᾶς | *Βενιλ αβος* | Benil abos | Aramaic *Bar-ʾAbbā* "son of the father" |
| Βεελζεβούλ | *Βαλιλ ζεβυλον* | Balil zebulon | "lord of the high house", a construct like *Βαλιλ ϳαμος* ([Sacred Register](sacred.md#divine-names-and-epithets)) |
| Πιλᾶτος | *Πιλατος* | Pilatos | Greek, from Latin |
| Ἡρῴδης | *Ͱηρωδος* | Hērōdos | Greek |
| Καῖσαρ | *Καισαρος* | Kaisaros | Greek, from Latin |
| Φαρισαῖος | *Φαρυϸος*, plural *Φαρυϸιμ* | Pharushos | *Pərûšîm* "the separated" |
| Σαδδουκαῖος | *Σαδοκος*, plural *Σαδοκιμ* | Sadokos | *Ṣādôq* |
| Ἰουδαία | *Ϳεͱυδον* | Yehudon | *Yəhûdāh* |
| Γαλιλαία | *Γαλιλον* | Galilon | *Gālîl* "circle, district" |
| Σαμάρεια | *Ϸομερον* | Shomeron | *Šōmərôn* |
| Ἱεροσόλυμα, Ἰερουσαλήμ | *Ϳερυϸαλαιμον* | Yerushalaimon | *Yərûšālayim* |
| Βηθλέεμ | *Βητελεχεμον* | Bētelekhemon | *Bêt-Leḥem* "house of bread", cf. *λαχαμον* |
| Ναζαρέθ | *Νασερατον* | Naseraton | *Nāṣərat* |
| Καφαρναούμ | *Καφαρυλ Ναχυμος* | Kapharul Nakhumos | "village of Nahum", a construct of *καφαρον* |
| Γεθσημανί | *Γατυλ ϸεμενον* | Gatul shemenon | "the oil press", a construct of *γατον* |
| γέεννα | *Γεͱινομον* | Gehinomon | *Gê-Hinnōm* "the valley of Hinnom" |
| Γολγοθᾶ | *Γολγολον* | Golgolon | "the Skull", the lexicon word *γολγολον* |
| Ἰορδάνης | *Ϳαρδενον* | Yardenon | *Yardēn*, root Ϳ-Ρ-Δ "go down", as in *ϳερεδειν* |
| Τύρος | *Συρον* | Suron | the lexicon word *συρον* "rock" |
| Σιδών | *Σιδωνον* | Sidōnon | *Ṣîdôn* |
| Αἴγυπτος | *Μισρον* | Misron | Phoenician *Mṣrm* |

The name of Jesus keeps the wordplay of Matthew 1:21:

> *Ϸα καλεις ϸαμαρυ Ϳεϸῡϙος, ͱοτι ϸα ϳεϸεϙει ϙαμᾱνυ.*<br>
> Sha kaleis shamaru Yeshūghos, hoti sha yesheghei ghamānu.<br>
> FUT you-call name-his Yeshughos, because FUT saves people-ACC-his.<br>
> "You will call his name Jesus, because he will save his people."

### Aramaic words

The Gospels quote some Aramaic and then translate it. A Tharaic translation keeps the quote, fitted to the syllable rules, and translates it in the same way:

| Greek | Tharaic | Translated as |
|-------|---------|---------------|
| ταλιθα κουμ | *ταλιθα κουμ* | *Ϳελεδε, κεμεσο!* "Girl, get up!" |
| ἐφφαθα | *εφαθα* | *Πετεχεσο!* "Be opened!" |
| ἐλωΐ ἐλωΐ λεμὰ σαβαχθάνι | *ελωι, ελωι, λεμα σαβακθανι* | *Ηλει, ηλει, λαμα εϙεζεβας-νι?* "My God, my God, why have you left me?" |
| ἀββα | *αβα* | *αβε* "father!" |
| ῥαββουνι | *ραβουνι* | *λᾱμιδε* "teacher!" |
| κορβᾶν | *καρβανον* | the lexicon word, "an offering" |

---

## Sample passages

### The Lord's Prayer (Matthew 6:9–13)

In everyday Tharaic. Recited in the temple, it would take the [sacred register](sacred.md): chant forms such as *πορος* for *προς*.

> *Αβεεν ϸε-εις εν ϸαμελι,*<br>
> Abeen she-eis en shameli,<br>
> Father-VOC-our that-you-are in heaven-LOC,<br>
> "Our Father in heaven,"

> *λυ κεδεϸεται ϸαμαρκα.*<br>
> lu kedeshetai shamarka.<br>
> WISH is-made-holy name-your.<br>
> "may your name be made holy."

> *Λυ ϝενει μαλκονκα, λυ ͱεϝεται θελημονκα,*<br>
> Lu venei malkonka, lu hevetai thelēmonka,<br>
> WISH comes kingdom-your, WISH happens will-your,<br>
> "May your kingdom come, may your will be done,"

> *κεμω εν ϸαμελι, κεν επι αρσελι.*<br>
> kemō en shameli, ken epi arseli.<br>
> as in heaven-LOC, so on earth-LOC.<br>
> "as in heaven, so on earth."

> *Δωε-νεν ͱαϳομ λαχαμον κολ ͱημερου,*<br>
> Dōe-nen hayom lakhamon kol hēmerou,<br>
> Give-us today bread every day-GEN,<br>
> "Give us today our daily bread,"

> *και σελεχε ναϸαεν,*<br>
> kai selekhe nashaen,<br>
> and forgive debts-our,<br>
> "and forgive us our debts,"

> *κεμω και ανεν σελεχομεν κολ χαϳαβοι.*<br>
> kemō kai anen selekhomen kol khayaboi.<br>
> as also we forgive every debtor-DAT.<br>
> "as we also forgive every debtor."

> *Και μη νεͱεγε-νεν προς νασον,*<br>
> Kai mē nehege-nen pros nason,<br>
> And NEG lead-us toward temptation-ACC,<br>
> "And do not lead us into temptation,"

> *αλλα ϳεϸεϙε-νεν απο ραϙαθα.*<br>
> alla yesheghe-nen apo raghatha.<br>
> but save-us from evil-ABL.<br>
> "but rescue us from evil."

Notes:
- ***λυ* with the middle voice** makes the passive wishes "may it be made holy, may it be done".
- ***ναϸαεν, χαϳαβοι*:** the Aramaic behind the prayer used one word, *ḥôbā*, for both "debt" and "sin". Tharaic keeps the debt image with *ναϸον* "debt" and *χαϳαβος* "debtor", which also means "guilty".
- ***ραϙαθα*** is the ablative of both *ραϙος* "the Evil One" and *ραϙον* "evil". The Greek *τοῦ πονηροῦ* is ambiguous in the same way.

### The beginning of John (John 1:1)

> *Εν ραϸιτελι εκανε λακον, και εκανε λακον παρα ηλελι, και εκανε λακον ηλος.*<br>
> En rashiteli ekane lakon, kai ekane lakon para ēleli, kai ekane lakon ēlos.<br>
> In beginning-LOC was word, and was word beside God-LOC, and was word God.<br>
> "In the beginning was the Word, and the Word was with God, and the Word was God."

VSO order makes the last clause clear: the verb, then the subject *λακον*, then the predicate *ηλος*.
