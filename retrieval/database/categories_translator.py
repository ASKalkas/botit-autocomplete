import os

from dotenv import load_dotenv

load_dotenv()

class CategoriesTranslator:
    def __init__(self):
        try:
            self.translations = self._read_translations_sheets()
        except Exception as e:
            self.translations = {}
