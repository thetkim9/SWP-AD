from google.cloud import translate_v2 as translate


destination_languages = {
    'Spanish': 'es',
    'Simplified Chinese': 'zh-CN',
    'Italian': 'it',
    'Hindi': 'hi',
    'Mongolian': 'mn',
    'Russian': 'ru',
    'Ukrainian': 'uk',
    'French': 'fr',
    'Indonesian': 'id',
    'Japanese': 'ja',
    'Slovak': 'sk',
    'Amharic':'am',
    'English':'en',
    'Korean' : 'ko'
}

class Translation:

    def __init__(self):
        self.translator = translate.Client()

    def translate(self, text, language):
        return self.translator.translate(text, target_language=destination_languages[language])['translatedText']

if __name__=="__main__":
    pass
