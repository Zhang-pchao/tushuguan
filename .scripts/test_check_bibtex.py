import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "check_bibtex", Path(__file__).with_name("check-bibtex.py")
)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CitationKeyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Path.cwd()
        self.directory = tempfile.TemporaryDirectory()
        os.chdir(self.directory.name)

    def tearDown(self):
        os.chdir(self.previous)
        self.directory.cleanup()

    def test_legacy_key_and_filename_are_preserved(self):
        path = Path("article/JMachLearnRes/VanDerMaaten_JMachLearnRes_2008_v9_p2579.bib")
        path.parent.mkdir(parents=True)
        original = "@article{JMLR:v9:vandermaaten08a, title={Example}}\n"
        path.write_text(original)
        checker.check_bibtex(path)
        self.assertEqual(path.read_text(), original)

    def test_standard_key_is_still_routed(self):
        path = Path("incoming.bib")
        path.write_text("@article{Example_JChemPhys_2026_v1_p1, title={Example}}\n")
        checker.check_bibtex(path)
        self.assertFalse(path.exists())
        self.assertTrue(Path("article/JChemPhys/Example_JChemPhys_2026_v1_p1.bib").is_file())

    def test_multiple_legacy_entries_are_rejected(self):
        path = Path("multiple.bib")
        path.write_text("@article{legacy:a, title={A}}\n@article{legacy:b, title={B}}\n")
        with self.assertRaisesRegex(ValueError, "More than one"):
            checker.check_bibtex(path)
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
