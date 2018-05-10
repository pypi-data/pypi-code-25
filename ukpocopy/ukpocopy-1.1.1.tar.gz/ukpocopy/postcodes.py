import re

from ukpocopy.validators import validate_postcode

POSTCODE_AREA_REGEX_PATTERN = "(^[a-zA-Z]+)"


class UKPostcode(object):
    __validator = validate_postcode

    def __init__(self, postcode):
        self.__validate(postcode)  # validates postcode before creation
        self.code = postcode.upper()

    @classmethod
    def __validate(cls, postcode):
        return cls.__validator(postcode)

    def __str__(self):
        return self.code

    @property
    def outward_code(self):
        return self.code.split(' ')[0]

    @property
    def inward_code(self):
        return self.code.split(' ')[1]

    @property
    def postcode_area(self):
        return re.match(POSTCODE_AREA_REGEX_PATTERN, self.outward_code).group(0)

    @property
    def postcode_district(self):
        return self.outward_code

    @property
    def postcode_sector(self):
        return "%s %s" % (self.outward_code, self.inward_code[0])

    @property
    def postcode_unit(self):
        return self.inward_code[-2:]
