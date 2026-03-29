from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EXIT_PHRASE = "exit please"


class SuiteError(ValueError):
    """Raised when a suite cannot be loaded or parsed."""


@dataclass(frozen=True)
class VocabularyEntry:
    source_word: str
    accepted_translations: tuple[str, ...]


def get_vocabulary_root() -> Path:
    return Path(__file__).resolve().parent.parent / "vocabulary"


def resolve_suite_path(language_code: str, suite_name: str, root: Path | None = None) -> Path:
    base_root = root or get_vocabulary_root()
    language_path = base_root / language_code
    if not language_path.is_dir():
        raise SuiteError(f"Language folder not found: {language_path}")

    suite_path = language_path / f"{suite_name}.txt"
    if not suite_path.is_file():
        raise SuiteError(f"Suite not found: {suite_path}")

    return suite_path


def parse_suite_line(raw_line: str, line_number: int) -> VocabularyEntry:
    if "|" not in raw_line:
        raise SuiteError(
            f"Malformed suite line {line_number}: expected 'word | translation1, translation2'"
        )

    source_word, translations_blob = (part.strip() for part in raw_line.split("|", maxsplit=1))
    if not source_word:
        raise SuiteError(f"Malformed suite line {line_number}: missing source word")

    translations = tuple(
        translation.strip() for translation in translations_blob.split(",") if translation.strip()
    )
    if not translations:
        raise SuiteError(f"Malformed suite line {line_number}: missing translations")

    return VocabularyEntry(source_word=source_word, accepted_translations=translations)


def load_suite(language_code: str, suite_name: str, root: Path | None = None) -> list[VocabularyEntry]:
    suite_path = resolve_suite_path(language_code, suite_name, root=root)
    entries: list[VocabularyEntry] = []

    for line_number, raw_line in enumerate(suite_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        entries.append(parse_suite_line(stripped, line_number))

    if not entries:
        raise SuiteError(f"Suite is empty: {suite_path}")

    return entries