import speech_recognition
from .translator import transolator
from upaj.settings import logging as logger
from .constants import ENGLISH_LANGUAGE_CODE

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()

    def get_audio_from_file(self, filename, language=ENGLISH_LANGUAGE_CODE):
        with speech_recognition.AudioFile(filename) as source:
            audio = self.recognizer.record(source)

        try:
            text = speech_recognition.recognize_google(audio, language)
            if language == ENGLISH_LANGUAGE_CODE:
                return text
            else: return translator.translate(text, language)
        except Exception as e:
            logger.error('Error while using VoiceRecognizer')

recognizer = VoiceRecognizer()
