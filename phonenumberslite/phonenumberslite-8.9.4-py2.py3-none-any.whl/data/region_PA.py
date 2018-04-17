"""Auto-generated file, do not edit by hand. PA metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_PA = PhoneMetadata(id='PA', country_code=507, international_prefix='00',
    general_desc=PhoneNumberDesc(national_number_pattern='[1-9]\\d{6,7}', possible_length=(7, 8)),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:1(?:0\\d|1[479]|2[37]|3[0137]|4[147]|5[05]|[68][58]|7[0167]|9[139])|2(?:[0235-79]\\d|1[0-7]|4[013-9]|8[026-9])|3(?:[089]\\d|1[014-7]|2[0-35]|3[03]|4[0-579]|55|6[068]|7[06-8])|4(?:00|3[0-79]|4\\d|7[0-57-9])|5(?:[01]\\d|2[0-7]|[56]0|79)|7(?:0[09]|2[0-26-8]|3[036]|4[04]|5[05-9]|6[05]|7[0-24-9]|8[7-9]|90)|8(?:09|2[89]|[34]\\d|5[0134]|8[02])|9(?:0[5-9]|1[0135-8]|2[036-9]|3[35-79]|40|5[0457-9]|6[05-9]|7[04-9]|8[35-8]|9\\d))\\d{4}', example_number='2001234', possible_length=(7,)),
    mobile=PhoneNumberDesc(national_number_pattern='(?:1[16]1|21[89]|8(?:1[01]|7[23]))\\d{4}|6(?:[02-9]\\d|1[0-5])\\d{5}', example_number='61234567', possible_length=(7, 8)),
    toll_free=PhoneNumberDesc(national_number_pattern='800\\d{4}', example_number='8001234', possible_length=(7,)),
    premium_rate=PhoneNumberDesc(national_number_pattern='(?:8(?:22|55|60|7[78]|86)|9(?:00|81))\\d{4}', example_number='8601234', possible_length=(7,)),
    number_format=[NumberFormat(pattern='(\\d{3})(\\d{4})', format='\\1-\\2', leading_digits_pattern=['[1-57-9]']),
        NumberFormat(pattern='(\\d{4})(\\d{4})', format='\\1-\\2', leading_digits_pattern=['6'])],
    mobile_number_portable_region=True)
