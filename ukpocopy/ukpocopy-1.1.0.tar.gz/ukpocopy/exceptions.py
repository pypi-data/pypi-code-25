class PostcodeValidationError(Exception):
    pass


class InvalidPostcodeFormatValidationError(PostcodeValidationError):
    """Given postcode format is invalid"""
    pass


class InvalidSingleDigitDistrictValidationError(PostcodeValidationError):
    """Given postcode area requires single district digit"""
    pass


class InvalidDoubleDigitDistrictValidationError(PostcodeValidationError):
    """Given postcode area requires double district digit"""
    pass


class InvalidZeroDigitForDistrictAreaValidationError(PostcodeValidationError):
    """Given postcode area does not allows 0 as district code digit"""
    pass


class InvalidTenDigitForDistrictAreaValidationError(PostcodeValidationError):
    """Given postcode area does not allows 10 as district code digit"""
    pass


class InvalidFirstPositionLetterValidationError(PostcodeValidationError):
    """Given postcode first position letter is invalid"""
    pass


class InvalidSecondPositionLetterValidationError(PostcodeValidationError):
    """Given postcode second position letter is invalid"""
    pass


class InvalidThirdPositionLetterValidationError(PostcodeValidationError):
    """Given postcode third position letter is invalid"""
    pass


class InvalidFourthPositionLetterValidationError(PostcodeValidationError):
    """Given postcode fourth position letter is invalid"""
    pass


class InvalidFinalTwoLettersError(PostcodeValidationError):
    """Given postcode two final letters are invalid"""
    pass


class InvalidCentralLondonSingleDigitDistrictValidationError(PostcodeValidationError):
    """Given Central London single digit district is invalid"""
    pass
