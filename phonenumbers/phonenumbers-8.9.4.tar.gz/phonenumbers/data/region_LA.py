"""Auto-generated file, do not edit by hand. LA metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_LA = PhoneMetadata(id='LA', country_code=856, international_prefix='00',
    general_desc=PhoneNumberDesc(national_number_pattern='[2-8]\\d{7,9}', possible_length=(8, 9, 10), possible_length_local_only=(6,)),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:2[13]|3(?:0\\d|[14])|[5-7][14]|41|8[1468])\\d{6}', example_number='21212862', possible_length=(8, 9), possible_length_local_only=(6,)),
    mobile=PhoneNumberDesc(national_number_pattern='20(?:2[2389]|5[24-689]|7[6-8]|9[125-9])\\d{6}', example_number='2023123456', possible_length=(10,)),
    national_prefix='0',
    national_prefix_for_parsing='0',
    number_format=[NumberFormat(pattern='(20)(\\d{2})(\\d{3})(\\d{3})', format='\\1 \\2 \\3 \\4', leading_digits_pattern=['20'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='([2-8]\\d)(\\d{3})(\\d{3})', format='\\1 \\2 \\3', leading_digits_pattern=['2[13]|3[14]|[4-8]'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='(30)(\\d{2})(\\d{2})(\\d{3})', format='\\1 \\2 \\3 \\4', leading_digits_pattern=['30'], national_prefix_formatting_rule='0\\1')])
