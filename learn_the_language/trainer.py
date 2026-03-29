from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Sequence

from learn_the_language.azure_translator import AzureTranslatorClient
from learn_the_language.suites import EXIT_PHRASE, VocabularyEntry


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]


@dataclass
class QuizResult:
    asked: int = 0
    correct: int = 0


class QuizExit(Exception):
    """Raised when the user asks to stop the quiz."""


def _read_answer(prompt: str, input_func: InputFunc) -> str:
    answer = input_func(prompt).strip()
    if answer == EXIT_PHRASE:
        raise QuizExit
    return answer


def run_quiz(
    entries: Sequence[VocabularyEntry],
    validator: AzureTranslatorClient,
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
    rng: random.Random | None = None,
) -> QuizResult:
    if not entries:
        raise ValueError("At least one vocabulary entry is required")

    randomizer = rng or random.Random()
    remaining = list(entries)
    randomizer.shuffle(remaining)
    result = QuizResult()

    while True:
        if not remaining:
            remaining = list(entries)
            randomizer.shuffle(remaining)

        entry = remaining.pop()
        result.asked += 1
        output_func(f"Translate to English: {entry.source_word}")

        first_answer = _read_answer("Your answer: ", input_func)
        if validator.is_correct_answer(entry, first_answer):
            result.correct += 1
            output_func("Correct.")
            continue

        output_func("Not quite. One more try.")
        second_answer = _read_answer("Your answer: ", input_func)
        if validator.is_correct_answer(entry, second_answer):
            result.correct += 1
            output_func("Correct.")
            continue

        expected = ", ".join(entry.accepted_translations)
        output_func(f"Correct translation: {expected}")
