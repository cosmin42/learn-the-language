from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from learn_the_language.azure_translator import AzureTranslatorClient, normalize_text
from learn_the_language.suites import EXIT_PHRASE, VocabularyEntry, format_entry, get_suite_output_path


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]


@dataclass(frozen=True)
class AddWordsResult:
    suite_path: Path
    added_entries: tuple[VocabularyEntry, ...]
    skipped_words: tuple[str, ...]


def prompt_for_words(
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> list[str]:
    output_func("Enter source words one per line. Submit an empty line to finish.")
    words: list[str] = []

    while True:
        word = input_func("Word: ").strip()
        if not word or word == EXIT_PHRASE:
            return words
        words.append(word)


def add_translated_words(
    language_code: str,
    suite_name: str,
    words: Iterable[str],
    translator: AzureTranslatorClient,
    *,
    root: Path | None = None,
) -> AddWordsResult:
    suite_path = get_suite_output_path(language_code, suite_name, root=root)
    suite_path.parent.mkdir(parents=True, exist_ok=True)

    existing_content = suite_path.read_text(encoding="utf-8") if suite_path.exists() else ""
    existing_words = {
        normalize_text(raw_line.split("|", maxsplit=1)[0])
        for raw_line in existing_content.splitlines()
        if raw_line.strip() and not raw_line.lstrip().startswith("#") and "|" in raw_line
    }

    seen_words = set(existing_words)
    added_entries: list[VocabularyEntry] = []
    skipped_words: list[str] = []

    for raw_word in words:
        word = raw_word.strip()
        normalized_word = normalize_text(word)
        if not normalized_word:
            continue
        if normalized_word in seen_words:
            skipped_words.append(word)
            continue

        translation = translator.translate(word, "en").strip()
        accepted_translations = tuple(
            item.strip() for item in translation.split(",") if item.strip()
        )
        if not accepted_translations:
            raise RuntimeError(f"Azure returned an empty translation for '{word}'")

        entry = VocabularyEntry(source_word=word, accepted_translations=accepted_translations)
        added_entries.append(entry)
        seen_words.add(normalized_word)

    if added_entries:
        lines_to_write = "\n".join(format_entry(entry) for entry in added_entries)
        prefix = ""
        if existing_content and not existing_content.endswith("\n"):
            prefix = "\n"
        suffix = "\n"
        with suite_path.open("a", encoding="utf-8") as handle:
            handle.write(prefix + lines_to_write + suffix)

    return AddWordsResult(
        suite_path=suite_path,
        added_entries=tuple(added_entries),
        skipped_words=tuple(skipped_words),
    )