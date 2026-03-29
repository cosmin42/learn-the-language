from __future__ import annotations

import random
import unittest

from learn_the_language.suites import VocabularyEntry
from learn_the_language.trainer import QuizExit, run_quiz


class StubValidator:
    def __init__(self, answers: dict[str, set[str]]) -> None:
        self.answers = answers

    def is_correct_answer(self, entry: VocabularyEntry, answer: str) -> bool:
        return answer in self.answers.get(entry.source_word, set())


class TrainerTestCase(unittest.TestCase):
    def test_run_quiz_counts_retry_success(self) -> None:
        prompts = iter(["wrong", "hello", "exit please"])
        output: list[str] = []
        entries = [VocabularyEntry("bonjour", ("hello",))]
        validator = StubValidator({"bonjour": {"hello"}})

        with self.assertRaises(QuizExit):
            run_quiz(
                entries,
                validator,
                input_func=lambda _prompt: next(prompts),
                output_func=output.append,
                rng=random.Random(0),
            )

        self.assertIn("Not quite. One more try.", output)
        self.assertIn("Correct.", output)

    def test_run_quiz_reveals_translation_after_two_wrong_answers(self) -> None:
        prompts = iter(["nope", "still nope", "exit please"])
        output: list[str] = []
        entries = [VocabularyEntry("merci", ("thank you", "thanks"))]
        validator = StubValidator({})

        with self.assertRaises(QuizExit):
            run_quiz(
                entries,
                validator,
                input_func=lambda _prompt: next(prompts),
                output_func=output.append,
                rng=random.Random(0),
            )

        self.assertIn("Correct translation: thank you, thanks", output)


if __name__ == "__main__":
    unittest.main()