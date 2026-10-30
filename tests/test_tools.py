"""Tests for the scripts in tools/. Run: python3 -m unittest discover -s tests"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))

from build_lexicon import DATA, parse, romanize  # noqa: E402
from check_phonotactics import problems  # noqa: E402
from check_texts import scan, tokens  # noqa: E402
from dialect import island  # noqa: E402
from greek import to_greek, to_roman  # noqa: E402
from inflect import Index, augment, paradigm, unaugment  # noqa: E402

ENTRIES = parse(DATA)
BY_HEAD = {e["greek"].split(" / ")[0]: e for e in ENTRIES}


def forms(word):
    return dict(paradigm(BY_HEAD[word]))


class GreekTest(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(to_greek("nāvei navos epi thāros"), "νᾱϝει ναϝος επι θᾱρος")
        self.assertEqual(to_greek("Yeshūghos"), "Ϳεϸῡϙος")
        self.assertEqual(to_roman("ϸαμον ϙερεβον"), "shamon gherebon")

    def test_round_trip(self):
        for e in ENTRIES:
            self.assertEqual(to_greek(romanize(e)), e["greek"], e["greek"])


class PhonotacticsTest(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(problems("ναϝος"), [])
        self.assertEqual(problems("τρια"), [])               # obstruent + ρ in everyday speech
        self.assertNotEqual(problems("τρια", chant=True), [])
        self.assertEqual(problems("ναϝιτ"), [])              # the construct ending -ιτ
        self.assertNotEqual(problems("ψυχᾱ"), [])
        self.assertEqual(problems("ψυχᾱ", high=True), [])


class DialectTest(unittest.TestCase):
    def test_island(self):
        self.assertEqual(island("τρια ναϝιμ"), "τιρια ναϝιμ")         # chant form
        self.assertEqual(island("ναϝιτ μᾱλικος"), "ναϝιτα μᾱλικος")  # construct vowel
        self.assertEqual(island("ϸα νᾱϝομεν"), "σα νᾱϝομεν")          # ϸ > σ


class InflectTest(unittest.TestCase):
    def test_nouns(self):
        self.assertEqual(forms("θᾱρος")["ABL.PL"], "θᾱραθις")
        self.assertEqual(forms("ναϝᾱ")["CONSTR"], "ναϝιτ")
        self.assertEqual(forms("βᾱσιλος")["CONSTR"], "βᾱσιλ")        # no *βᾱσιλιλ
        self.assertEqual(forms("κασαφευς")["VOC.SG"], "κασαφευ")
        self.assertEqual(forms("κασαφευς")["GEN.SG"], "κασαφεϝι")
        self.assertEqual(forms("ποιημα")["DAT.PL"], "ποιημασι")
        self.assertEqual(forms("γᾱ")["LOC.SG"], "γᾱελι")             # sea cases on the whole word
        self.assertEqual(forms("ισχολᾱ")["GEN.SG"], "ισχολις")      # everyday Doric word
        self.assertEqual(forms("σχολᾱ")["GEN.SG"], "σχολᾱς")
        self.assertNotIn("CONSTR", forms("δᾱμος"))                  # no construct for Doric nouns

    def test_verbs(self):
        self.assertEqual(forms("νᾱϝειν")["AOR.1SG"], "ενᾱϝα")
        self.assertEqual(forms("νᾱϝειν")["PTCP.AOR AN.NOM.SG"], "νᾱϝαντος")
        self.assertEqual(forms("φερειν")["MID.AOR.3PL"], "εφεραντο")
        self.assertEqual(forms("ποιειν")["PRES.3PL"], "ποιοντι")
        self.assertEqual(forms("ποιειν")["AOR.1PL"], "εποιησαμες")
        self.assertEqual(forms("ερχεσθαι")["MID.PRES.1PL"], "ερχομεσθα")
        self.assertEqual(forms("κανειν")["PRES.3SG ε(σ)-"], "εσι")
        self.assertEqual(forms("κανειν")["PRES.3SG"], "κανει")           # after ϸα and ϝα-

    def test_augment(self):
        self.assertEqual(augment("νᾱϝ"), "ενᾱϝ")
        self.assertEqual(augment("αγ"), "ᾱγ")
        self.assertEqual(augment("ειδ"), "ειδ")
        self.assertEqual(unaugment("εποιησ", "ποι"), "ποιησ")
        self.assertEqual(unaugment("μετενοησ", "μετανο"), "μετανοησ")
        self.assertEqual(unaugment("ᾱρξ", "αρχ"), "αρξ")
        self.assertEqual(unaugment("ευξ", "ευχ"), "ευξ")

    def test_analyze(self):
        index = Index()
        self.assertIn(("βλεπειν", "AOR.3SG"), index.analyze("εβλεψε"))
        self.assertIn(("λεκειν", "AOR.3SG"), index.analyze("ελεκε-ιμ"))       # object enclitic
        self.assertIn(("κανειν", "PRES.3SG ε(σ)-"), index.analyze("ϸε-εσι-υ"))      # prefix and enclitic
        self.assertIn(("ͱοδος", "ACC.SG +κα"), index.analyze("ͱοδονκα"))     # possessive enclitic
        self.assertIn(("Ϳεϸῡϙος", "VOC.SG"), index.analyze("Ϳεϸῡϙε"))        # a name
        self.assertEqual(index.analyze("ναϝοτ"), [])


class CheckTextsTest(unittest.TestCase):
    def test_skips(self):
        line = "*ναϝος*, root Ν-Ϝ, ending *-ιλ*, not \\*βᾱσιλιλ, Greek *ἄστρα*, the letter *ᾱ*"
        self.assertEqual([w for w, _ in tokens(line)], ["ναϝος"])

    def test_skip_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "text.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("*ναϝος* and *νᾱϝουσα* <!-- check_texts: skip νᾱϝουσα -->\n*νᾱϝουσα*\n")
            self.assertEqual([(n, w) for _, n, w in scan([path], Index())], [(2, "νᾱϝουσα")])


if __name__ == "__main__":
    unittest.main()
