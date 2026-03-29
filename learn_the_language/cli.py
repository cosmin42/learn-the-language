from __future__ import annotations

import argparse
import sys

import requests

from learn_the_language.azure_translator import AzureTranslatorClient
from learn_the_language.suites import SuiteError, load_suite
from learn_the_language.trainer import QuizExit, run_quiz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vocabulary trainer with Azure-backed validation")
    parser.add_argument("language", help="ISO639 language folder name, for example fr or es")
    parser.add_argument("suite", help="Suite file name without the .txt suffix")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        entries = load_suite(args.language, args.suite)
        validator = AzureTranslatorClient(language_code=args.language)
        result = run_quiz(entries, validator)
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

    print(f"Session ended. Score: {result.correct}/{result.asked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())