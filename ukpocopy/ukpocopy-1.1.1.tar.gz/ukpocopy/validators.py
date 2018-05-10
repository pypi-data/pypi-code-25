import re

from ukpocopy.exceptions import InvalidSingleDigitDistrictValidationError, \
    InvalidDoubleDigitDistrictValidationError, InvalidZeroDigitForDistrictAreaValidationError, \
    InvalidTenDigitForDistrictAreaValidationError, PostcodeValidationError, \
    InvalidFirstPositionLetterValidationError, InvalidSecondPositionLetterValidationError, \
    InvalidThirdPositionLetterValidationError, InvalidFourthPositionLetterValidationError, \
    InvalidFinalTwoLettersError, InvalidPostcodeFormatValidationError, \
    InvalidCentralLondonSingleDigitDistrictValidationError

POSTCODE_AREA_REGEX_PATTERN = "(^[a-zA-Z]+)"
POSTCODE_DISTRICT_DIGITS_REGEX_PATTERN = "^[a-zA-Z]+(\d{1,2})"
A9A_REGEX_PATTERN = '^[a-zA-Z]\d[a-zA-Z]\s'
AA9A_REGEX_PATTERN = '^[a-zA-Z]{2}\d[a-zA-Z]\s'
A9A_or_AA9A_REGEX_PATTERN = "^[a-zA-Z]{1,2}\d[a-zA-Z]"


AREAS_WITH_ONLY_SINGLE_DIGIT_DISTRICT = [
    "BR", "FY", "HA", "HD", "HG", "HR", "HS", "HX", "JE", "LD", "SM", "SR", "WC", "WN", "ZE"
]
AREAS_WITH_ONLY_DOUBLE_DIGIT_DISTRICT = ["AB", "LL", "SO"]
AREAS_WITH_ZERO_DIGIT_DISTRICT = ["BL", "BS", "CM", "CR", "FY", "HA", "PR", "SL", "SS"]

CENTRAL_LONDON_SINGLE_DIGIT_DISTRICTS_WITHOUT_LAST_LETTER = [
    "EC1", "EC2", "EC3", "EC4", "SW1", "W1", "WC1", "WC2"
]

OTHER_POSSIBLE_CENTRAL_LONDON_SINGLE_DIGIT_DISTRICTS_WITH_LAST_LETTER = [
    "E1W", "N1C", "N1P", "NW1W", "SE1P"
]

VALID_THIRD_POSITION_LETTERS_FOR_A9A_FORMAT = [
    "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "P", "S", "T", "U", "W"
]

VALID_FOURTH_POSITION_LETTERS_FOR_AA9A_FORMAT = [
    "A", "B", "E", "H", "M", "N", "P", "R", "V", "W", "X", "Y"
]

INVALID_FINAL_LETTERS = ["C", "I", "K", "M", "O", "V"]


def validate_postcode(code):
    validate_rules = [
        validate_postcode_using_regex,
        validate_single_digit_district,
        validate_double_digit_district,
        validate_zero_district,
        validate_first_position_letter,
        validate_second_position_letter,
        validate_third_position_letter,
        validate_fourth_position_letter,
        validate_final_two_letters,
        validate_central_london_single_digit_district
    ]

    for validate_rule in validate_rules:
        try:
            validate_rule(code)
        except PostcodeValidationError as e:
            raise e


def validate_postcode_using_regex(code):
    UK_POSTCODE_REGEX = "^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})" \
                        "|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])" \
                        "|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$"

    if not re.match(UK_POSTCODE_REGEX, code):
        raise InvalidPostcodeFormatValidationError


def validate_single_digit_district(code):
    area = _retrieve_postcode_area(code)
    district_digits = _retrieve_postcode_district_digits(code)

    if area in AREAS_WITH_ONLY_SINGLE_DIGIT_DISTRICT and len(district_digits) != 1:
        raise InvalidSingleDigitDistrictValidationError


def validate_double_digit_district(code):
    area = _retrieve_postcode_area(code)
    district_digits = _retrieve_postcode_district_digits(code)

    if area in AREAS_WITH_ONLY_DOUBLE_DIGIT_DISTRICT and len(district_digits) != 2:
        raise InvalidDoubleDigitDistrictValidationError


def validate_zero_district(code):
    area = _retrieve_postcode_area(code)
    district_digits = _retrieve_postcode_district_digits(code)

    if area not in AREAS_WITH_ZERO_DIGIT_DISTRICT and district_digits == '0':
        raise InvalidZeroDigitForDistrictAreaValidationError

    if area in AREAS_WITH_ZERO_DIGIT_DISTRICT and area != 'BS' and district_digits == '10':
        raise InvalidTenDigitForDistrictAreaValidationError


def validate_first_position_letter(code):
    first_position_letter = code[0].upper()

    if first_position_letter in ['Q', 'V', 'X']:
        raise InvalidFirstPositionLetterValidationError


def validate_second_position_letter(code):
    second_position_letter = code[1].upper()

    if second_position_letter in ['I', 'J', 'Z']:
        raise InvalidSecondPositionLetterValidationError


def validate_third_position_letter(code):
    third_position_letter = code[2].upper()

    if re.match(A9A_REGEX_PATTERN, code) and \
            third_position_letter not in VALID_THIRD_POSITION_LETTERS_FOR_A9A_FORMAT:
        raise InvalidThirdPositionLetterValidationError


def validate_fourth_position_letter(code):
    fourth_position_letter = code[3].upper()

    if re.match(AA9A_REGEX_PATTERN, code) and \
            fourth_position_letter not in VALID_FOURTH_POSITION_LETTERS_FOR_AA9A_FORMAT:
        raise InvalidFourthPositionLetterValidationError


def validate_final_two_letters(code):
    last_letter = code[-1].upper()
    next_to_last_letter = code[-2].upper()

    if last_letter in INVALID_FINAL_LETTERS or next_to_last_letter in INVALID_FINAL_LETTERS:
        raise InvalidFinalTwoLettersError


def validate_central_london_single_digit_district(code):
    if re.match(A9A_or_AA9A_REGEX_PATTERN, code):
        postcode_district = _retrieve_postcode_district(code)
        district_code_without_last_letter = postcode_district[:-1]

        if district_code_without_last_letter not in CENTRAL_LONDON_SINGLE_DIGIT_DISTRICTS_WITHOUT_LAST_LETTER:
            if postcode_district in OTHER_POSSIBLE_CENTRAL_LONDON_SINGLE_DIGIT_DISTRICTS_WITH_LAST_LETTER:
                return None

            raise InvalidCentralLondonSingleDigitDistrictValidationError


def _retrieve_postcode_district(code):
    return code.split(' ')[0].upper()


def _retrieve_postcode_area(code):
    area = None
    re_match = re.match(POSTCODE_AREA_REGEX_PATTERN, code)

    if re_match:
        area = re_match.group(0).upper()

    return area


def _retrieve_postcode_district_digits(code):
    district_digits = None
    re_match = re.match(POSTCODE_DISTRICT_DIGITS_REGEX_PATTERN, code)

    if re_match:
        district_digits = re_match.group(1)

    return district_digits
