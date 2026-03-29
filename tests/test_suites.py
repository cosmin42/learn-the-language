from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from learn_the_language.suites import SuiteError, load_suite, parse_suite_line, resolve_suite_path


class SuitesTestCase(unittest.TestCase):
    def test_parse_suite_line_with_multiple_translations(self) -> None:
        entry = parse_suite_line("bonjour | hello, good morning", 3)

        self.assertEqual(entry.source_word, "bonjour")
        self.assertEqual(entry.accepted_translations, ("hello", "good morning"))

    def test_parse_suite_line_rejects_missing_separator(self) -> None:
        with self.assertRaises(SuiteError):
            parse_suite_line("bonjour hello", 2)

    def test_load_suite_ignores_comments_and_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            suite_dir = root / "fr"
            suite_dir.mkdir(parents=True)
            (suite_dir / "basics.txt").write_text(
                "# greetings\n\nbonjour | hello\nmerci | thank you, thanks\n",
                encoding="utf-8",
            )

            entries = load_suite("fr", "basics", root=root)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1].accepted_translations, ("thank you", "thanks"))

    def test_resolve_suite_path_requires_language_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(SuiteError):
                resolve_suite_path("fr", "basics", root=Path(temp_dir))


if __name__ == "__main__":
    unittest.main()