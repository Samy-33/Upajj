from google.cloud import translate
from .constants import HINDI_LANGUAGE_CODE, FLOW_KEY_TRANSLATION_MAP
from upaj.settings import logging as logger


class Translator:
    def __init__(self):
        self.client = translate.Client()

    def translate(self, text, target_lang=HINDI_LANGUAGE_CODE):
        translation = self.client.translate(text, target_language=target_lang)
        logger.debug(f'Translation for {text} to {target_lang}: {translation["translatedText"]}')
        return translation['translatedText']

    def get_option_translation(self, flow_key, target_language):
        flow_key_values = FLOW_KEY_TRANSLATION_MAP.get(flow_key)
        if flow_key_values and target_language in flow_key_values:
            translation = flow_key_values[target_language]
            logger.debug(f'translation for {flow_key} to {target_language}: {translation}')
            return translation

        raise Exception(f'Invalid Flow Key: {flow_key} or target_language: {target_language}')

translator = Translator()
