import enchant
import urlparse
import urllib
from enchant.utils import get_default_language
from enchant.checker import SpellChecker


class CKEnchanter(SpellChecker):
    def __init__(self, lang=None, *args, **kwargs):
        """
        Initialize a new CKEnchanter object
        """

        # Make sure the desired default dictionary exists
        # if it doesn't, get the default language
        if lang is None:
            lang = get_default_language()

        # If a word list was given, add it to the default dictionary
        if kwargs.get('wl_path', None):
            master_dict = enchant.DictWithPWL(lang, kwargs.pop('wl_path'))
        else:
            master_dict = lang

        # Finish creating a pyenchant spellchecker
        SpellChecker.__init__(self, master_dict, *args, **kwargs)

    def _get_data_val(self, data, key):
        """
        Get a key out of the ckeditor's data string
        """
        val = data.get(key, [])
        if len(val) > 0:
            return val[0]
        return ''

    def parse_ckeditor_request(self, request_data):
        """
        Parses a request from CKEdtior and prepares the appropriate response
        """
        # Break apart the query string
        data = urlparse.parse_qs(request_data)
        cmd = self._get_data_val(data, 'cmd')

        if cmd == 'getbanner':
            # CKEditor banner response
            return {"banner": True}
        elif cmd == 'get_lang_list' or cmd == 'get_info':
            # CKEditor langList response
            return {
                "langList": {
                    "ltr": {
                        "en_US": "American English",
                    },
                    "rtl": {}
                },
                "verLang": 6
            }
        elif self._get_data_val(data, 'cmd') == 'check_spelling':
            # Ok, now we're actually checking the text
            text = urllib.unquote(self._get_data_val(data, 'text')).replace(',', ' ')
            return self.spellcheck(text)

        # For safety
        return {}

    def spellcheck(self, text):
        # Run the spellchecker
        self.set_text(text)

        errors = []
        for err in self:
            suggestions = self.dict.suggest(err.word)
            result = {
                'word': err.word,
                'ud': 'false',
                'suggestions': suggestions
            }
            errors.append(result)

        return errors
