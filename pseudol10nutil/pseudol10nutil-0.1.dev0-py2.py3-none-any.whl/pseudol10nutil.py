import six

from . import transforms


class PseudoL10nUtil:

    def __init__(self):
        self.transforms = [
            transforms.transliterate_diacritic,
            transforms.pad_length,
            transforms.square_brackets
            ]

    def pseudolocalize(self, s):
        if not isinstance(s, six.text_type):
            raise TypeError("String to pseudo-localize must be of type '{0}'.".format(six.text_type.__name__))
        result = s
        for munge in self.transforms:
            result = munge(result)
        return result
