from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import requests

from learn_the_language.suites import VocabularyEntry


def normalize_text(text: str) -> str:
    normalized = text.casefold().strip()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return " ".join(normalized.split())


@dataclass
class AzureTranslatorClient:
    language_code: str
    endpoint: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com"
        )
    )
    key: str | None = field(default_factory=lambda: os.getenv("AZURE_TRANSLATOR_KEY"))
    region: str | None = field(default_factory=lambda: os.getenv("AZURE_TRANSLATOR_REGION"))

    def __post_init__(self) -> None:
        if not self.key:
            raise RuntimeError("Environment variable AZURE_TRANSLATOR_KEY is required")
        self._translation_cache: dict[tuple[str, str], str] = {}

    def translate(self, text: str, to_language: str) -> str:
        cache_key = (text, to_language)
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]

        url = self.endpoint.rstrip("/") + "/translate"
        params = {"api-version": "3.0", "to": to_language}
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Content-Type": "application/json",
        }
        if self.region:
            headers["Ocp-Apim-Subscription-Region"] = self.region

        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=[{"text": text}],
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        translations: list[str] = []
        for item in payload:
            for translation in item.get("translations", []):
                text_value = translation.get("text", "").strip()
                if text_value:
                    translations.append(text_value)

        translated_text = ", ".join(translations)
        self._translation_cache[cache_key] = translated_text
        return translated_text

    def is_correct_answer(self, entry: VocabularyEntry, answer: str) -> bool:
        normalized_answer = normalize_text(answer)
        if not normalized_answer:
            return False

        accepted = {normalize_text(item) for item in entry.accepted_translations}
        if normalized_answer in accepted:
            return True

        azure_translation = normalize_text(self.translate(entry.source_word, "en"))
        if normalized_answer == azure_translation:
            return True

        back_translation = normalize_text(self.translate(answer, self.language_code))
        source_normalized = normalize_text(entry.source_word)
        return back_translation == source_normalized