from __future__ import annotations

import argparse
import sys

import requests

from learn_the_language.azure_translator import AzureTranslatorClient
from learn_the_language.suite_builder import add_translated_words, prompt_for_words
from learn_the_language.suites import SuiteError, load_suite
from learn_the_language.trainer import QuizExit, run_quiz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vocabulary trainer with Azure-backed validation")
    subparsers = parser.add_subparsers(dest="command")

    quiz_parser = subparsers.add_parser("quiz", help="Start a quiz for an existing suite")
    quiz_parser.add_argument("language", help="ISO639 language folder name, for example fr or es")
    quiz_parser.add_argument("suite", help="Suite file name without the .txt suffix")

    add_parser = subparsers.add_parser("add", help="Create or extend a suite using Azure English translations")
    add_parser.add_argument("language", help="ISO639 language folder name, for example fr or es")
    add_parser.add_argument("suite", help="Suite file name without the .txt suffix")
    add_parser.add_argument("words", nargs="*", help="Source words to add to the suite")
    return parser


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    raw_args = sys.argv[1:]
    if raw_args and raw_args[0] not in {"quiz", "add", "-h", "--help"}:
        raw_args = ["quiz", *raw_args]
    return parser.parse_args(raw_args)


def run_quiz_command(language: str, suite: str) -> int:
    entries = load_suite(language, suite)
    validator = AzureTranslatorClient(language_code=language)
    result = run_quiz(entries, validator)
    print(f"Session ended. Score: {result.correct}/{result.asked}")
    return 0


def run_add_command(language: str, suite: str, words: list[str]) -> int:
    source_words = words or prompt_for_words()
    if not source_words:
        print("No words were provided.", file=sys.stderr)
        return 1

    translator = AzureTranslatorClient(language_code=language)
    result = add_translated_words(language, suite, source_words, translator)

    if result.added_entries:
        print(f"Added {len(result.added_entries)} word(s) to {result.suite_path}")
    else:
        print(f"No new words were added to {result.suite_path}")

    if result.skipped_words:
        skipped = ", ".join(result.skipped_words)
        print(f"Skipped duplicate word(s): {skipped}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parse_args(parser)

    try:
        if args.command is None and not hasattr(args, "language"):
            parser.print_help()
            return 1
        if args.command in (None, "quiz"):
            return run_quiz_command(args.language, args.suite)
        if args.command == "add":
            return run_add_command(args.language, args.suite, args.words)
        parser.print_help()
        return 1
    except SuiteError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as exc:
        print(f"Azure Translator request failed: {exc}", file=sys.stderr)
        return 1
    except QuizExit:
        print("Session ended by user.")
        return 0
    except KeyboardInterrupt:
        print("\nSession interrupted.")
        return 0
    except EOFError:
        print("\nSession ended.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())