import phonenumbers
from cargo.validators import NullValidator, Validator


__all__ = 'PhoneNumberValidator',


class PhoneNumberValidator(NullValidator):
    __slots__ = Validator.__slots__
    FORMAT_CODE = 7805

    def validate_number(self):
        if phonenumbers.phonenumberutil.is_possible_number(self.value):
            return True
        self.set_value_error(self.FORMAT_CODE,
                             "phone number is malformed ({})",
                             self.value)
        return False

    def validate(self):
        if self.is_nullable():
            return True
        try:
            assert self.validate_null()
            return self.validate_number()
        except AssertionError:
            return False
