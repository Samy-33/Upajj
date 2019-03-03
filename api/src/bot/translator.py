from google.cloud import translate
from .constants import HINDI_LANGUAGE_CODE, FLOW_KEY_TRANSLATION_MAP
from upaj.settings import logging as logger


class Translator:
    def __init__(self):
        self.client = translate.Client()

    def translate(self, text, target_lang=HINDI_LANGUAGE_CODE):
        logger.debug(f'Got text: {text} and target_lang: {target_lang}')
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

    def get_all_option_translations(self, option_list, target_language):
        response_list = self.client.translate(option_list, target_language=target_language)
        logger.debug(f'Translation for {option_list}: {response_list}')
        translated_options = list(translation['translatedText'] for translation in response_list)
        return translated_options

translator = Translator()
