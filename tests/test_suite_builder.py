from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from learn_the_language.suite_builder import add_translated_words, prompt_for_words


class StubTranslator:
    def __init__(self, translations: dict[str, str]) -> None:
        self.translations = translations

    def translate(self, text: str, to_language: str) -> str:
        if to_language != "en":
            raise AssertionError("StubTranslator only supports English translations")
        return self.translations[text]


class SuiteBuilderTestCase(unittest.TestCase):
    def test_prompt_for_words_stops_on_blank_line(self) -> None:
        prompts = iter(["hallo", "goedemorgen", ""])
        messages: list[str] = []

        words = prompt_for_words(
            input_func=lambda _prompt: next(prompts),
            output_func=messages.append,
        )

        self.assertEqual(words, ["hallo", "goedemorgen"])
        self.assertEqual(messages, ["Enter source words one per line. Submit an empty line to finish."])

    def test_add_translated_words_creates_new_suite_file(self) -> None:
        translator = StubTranslator({"hallo": "hello", "fiets": "bicycle, bike"})

        with tempfile.TemporaryDirectory() as temp_dir:
            result = add_translated_words(
                "nl",
                "travel",
                ["hallo", "fiets"],
                translator,
                root=Path(temp_dir),
            )
            written = (Path(temp_dir) / "nl" / "travel.txt").read_text(encoding="utf-8")

        self.assertEqual(len(result.added_entries), 2)
        self.assertEqual(written, "hallo | hello\nfiets | bicycle, bike\n")

    def test_add_translated_words_skips_existing_duplicates(self) -> None:
        translator = StubTranslator({"fiets": "bicycle", "boek": "book"})

        with tempfile.TemporaryDirectory() as temp_dir:
            suite_dir = Path(temp_dir) / "nl"
            suite_dir.mkdir(parents=True)
            (suite_dir / "basics.txt").write_text("fiets | bicycle\n", encoding="utf-8")

            result = add_translated_words(
                "nl",
                "basics",
                ["fiets", "boek", "boek"],
                translator,
                root=Path(temp_dir),
            )
            written = (suite_dir / "basics.txt").read_text(encoding="utf-8")

        self.assertEqual(result.skipped_words, ("fiets", "boek"))
        self.assertEqual(len(result.added_entries), 1)
        self.assertEqual(written, "fiets | bicycle\nboek | book\n")


if __name__ == "__main__":
    unittest.main()