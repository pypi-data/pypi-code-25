import abc
import validators


class BaseField:
    __metaclass__ = abc.ABCMeta

    def __init__(self, required=False):
        self.value = None
        self.required = required
        self.errors = []

    def set_value(self, value):
        self.value = value

    def validate(self):
        if self.value is None or self.value == '':
            self.clean_required()
        else:
            self.clean()
        return self.errors

    def clean_required(self):
        if self.required:
            self.errors.append('is require')

    @abc.abstractmethod
    def clean(self):
        pass


class IntField(BaseField):
    def clean(self):
        try:
            self.value = int(self.value)
        except (ValueError, TypeError):
            self.errors.append('is not integer')


class ChoiceField(BaseField):
    def __init__(self,  choices, required=False):
        super().__init__(required)
        self.choices = choices

    def clean(self):
        if self.value not in self.choices:
            str_choices = ', '.join(self.choices)
            self.errors.append('choice one of %s' % str_choices)


class CharField(BaseField):
    def clean(self):
        if not isinstance(self.value, str):
            self.errors.append('is not string')
            return False


class XmlUriField(CharField):
    def clean(self):
        if super().clean() is not False:
            if not self.value.endswith('.xml'):
                self.errors.append('is not xml')


class EmailField(CharField):
    def clean(self):
        if super().clean() is not False:
            if validators.email(self.value) is not True:
                self.errors.append('bad email')


class UrlField(CharField):
    def clean(self):
        if super().clean() is not False:
            if validators.url(self.value) is not True:
                self.errors.append('bad url')
