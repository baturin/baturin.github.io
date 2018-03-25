
class Language(object):
    def __init__(self, code, description):
        self._code = code
        self._description = description

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description


class Languages(object):
    _all_languages = [
        Language('en', 'English'),
        Language('fr', 'French'),
        Language('ru', 'Russian'),
        Language('de', 'German'),
        Language('es', 'Spanish'),
    ]

    @staticmethod
    def get_all_languages():
        return Languages._all_languages
