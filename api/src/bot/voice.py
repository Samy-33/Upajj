import speech_recognition
import goslate
from upaj.settings import logging as logger

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.slate = goslate.Goslate()

    def get_audio_from_file(self, filename, language='en-EN'):
        with speech_recognition.AudioFile(filename) as source:
            audio = self.recognizer.record(source)

        try:
            text = speech_recognition.recognize_google(audio, language)
            if language == 'en-EN':
                return text
            else: return goslate.translate(text, language)
        except Exception as e:
            logger.error('Error while using VoiceRecognizer')

recognizer = VoiceRecognizer()
