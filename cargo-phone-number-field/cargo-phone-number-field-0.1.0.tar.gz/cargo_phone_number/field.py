import phonenumbers
import psycopg2
from psycopg2.extensions import register_adapter, adapt
from cargo.fields import Field
from cargo.fields.extras import _DurationAdapter
from cargo.expressions import StringLogic
from .validator import PhoneNumberValidator


__all__ = 'PhoneNumber',


class _PhoneNumberAdapter(_DurationAdapter):

    def getquoted(self):
        adapter = adapt(PhoneNumber._db_re.sub("", phonenumbers.format_number(
            self.value, PhoneNumber.INTERNATIONAL)).replace('ext', 'x'))
        adapter.prepare(self.conn)
        return adapter.getquoted()


class PhoneNumber(Field, StringLogic):
    OID = TEXT
    __slots__ = ('field_name', 'primary', 'unique', 'index', 'not_null',
                 'value', 'validator', '_alias', 'default', 'table',
                 'region')
    INTERNATIONAL = phonenumbers.PhoneNumberFormat.INTERNATIONAL
    NATIONAL = phonenumbers.PhoneNumberFormat.NATIONAL
    RFC3966 = phonenumbers.PhoneNumberFormat.RFC3966
    E164 = phonenumbers.PhoneNumberFormat.E164

    def __init__(self, region='US', *args, validator=PhoneNumberValidator,
                 **kwargs):
        """`Phone Number`
            ==================================================================
            @region: (#str) 2-letter uppercase ISO 3166-1 country
                code (e.g. "GB")
            ==================================================================
            :see::meth:Field.__init__
        """
        self.region = region
        super().__init__(*args, validator=validator, **kwargs)

    def __call__(self, value=Field.empty):
        """ @value: (#str) phone number-like string or
                :class:phonenumbers.PhoneNumber
        """
        if value is not self.empty:
            if value is not None:
                value = phonenumbers.parse(str(value), self.region)
                value.__str__ = value.__unicode__ = self.to_std
            self.value = value
        return self.value

    def format(self, format=NATIONAL):
        return phonenumbers.format_number(self.value, format)

    def for_json(self):
        if self.value_is_not_null:
            return self.to_std()
        return None

    def to_html(self):
        return phonenumbers.format_number(self.value, self.RFC3966)

    def to_std(self):
        return phonenumbers.format_number(self.value, self.E164)

    def from_text(self, text):
        for m in phonenumbers.PhoneNumberMatcher(text, self.region):
            return self.__call__(m.raw_string)

    _db_re = re.compile(r"""[\-\s\.]+""")

    @staticmethod
    def register_adapter():
        register_adapter(phonenumbers.phonenumber.PhoneNumber,
                         _PhoneNumberAdapter)
