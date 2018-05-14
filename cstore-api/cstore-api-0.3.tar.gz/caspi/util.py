import re


def snake_str_to_pascal_str(src):
    return "".join([word[0].upper() + word[1:] for word in src.split('_')])


def escape_unit_suffix(src):
    return "".join(re.findall('\d+', src))
