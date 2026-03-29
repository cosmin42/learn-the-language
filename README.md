# Learn The Language

This repository contains a small CLI script that quizzes vocabulary from plain-text suites stored by ISO639 language code.

## Vocabulary layout

Store suite files under `vocabulary/<iso639>/<suite>.txt`.

Each non-empty line must use this format:

```text
word | translation1, translation2
```

Example:

```text
bonjour | hello, good morning
merci | thank you, thanks
```

## Azure configuration

The script uses the Azure Translator Text API and reads the same environment variables as the existing helper you referenced:

- `AZURE_TRANSLATOR_KEY` (required)
- `AZURE_TRANSLATOR_REGION` (optional)
- `AZURE_TRANSLATOR_ENDPOINT` (optional, defaults to `https://api.cognitive.microsofttranslator.com`)

## Usage

Run directly as a module:

```bash
python -m learn_the_language.cli fr basics
```

Or install the package and use the console script:

```bash
pip install -e .
learn-the-language fr basics
```

During the quiz, type `exit please` to stop immediately.

## Validation behavior

For each shown foreign-language word, the script:

1. checks the answer against the accepted translations from the suite file
2. checks Azure's English translation for the word
3. uses one retry after the first wrong answer
4. reveals the accepted translations after the second wrong answer and moves on