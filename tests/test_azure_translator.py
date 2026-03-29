from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from learn_the_language.azure_translator import AzureTranslatorClient, normalize_text
from learn_the_language.suites import VocabularyEntry


class AzureTranslatorTestCase(unittest.TestCase):
    def test_normalize_text_strips_case_and_punctuation(self) -> None:
        self.assertEqual(normalize_text(" Hello, World! "), "hello world")

    def test_is_correct_answer_accepts_suite_translation(self) -> None:
        client = AzureTranslatorClient(language_code="fr", key="secret")
        entry = VocabularyEntry(source_word="bonjour", accepted_translations=("hello",))

        self.assertTrue(client.is_correct_answer(entry, "Hello"))

    @patch("learn_the_language.azure_translator.requests.post")
    def test_is_correct_answer_accepts_azure_translation(self, post_mock: Mock) -> None:
        response = Mock()
        response.json.return_value = [{"translations": [{"text": "thank you"}]}]
        response.raise_for_status.return_value = None
        post_mock.return_value = response

        client = AzureTranslatorClient(language_code="fr", key="secret")
        entry = VocabularyEntry(source_word="merci", accepted_translations=("thanks",))

        self.assertTrue(client.is_correct_answer(entry, "thank you"))

    @patch("learn_the_language.azure_translator.requests.post")
    def test_is_correct_answer_accepts_back_translation(self, post_mock: Mock) -> None:
        first_response = Mock()
        first_response.json.return_value = [{"translations": [{"text": "greetings"}]}]
        first_response.raise_for_status.return_value = None

        second_response = Mock()
        second_response.json.return_value = [{"translations": [{"text": "bonjour"}]}]
        second_response.raise_for_status.return_value = None

        post_mock.side_effect = [first_response, second_response]

        client = AzureTranslatorClient(language_code="fr", key="secret")
        entry = VocabularyEntry(source_word="bonjour", accepted_translations=("hello",))

        self.assertTrue(client.is_correct_answer(entry, "greetings"))


if __name__ == "__main__":
    unittest.main()