OPERATORS = {
  "IS": "is",
  "IN": "[in[",
  "GTE": ">=",
  "LT": "<"
}

OPERATORS_FUNCTION = {
  OPERATORS["IS"]: lambda context, value: context == value,
  OPERATORS["GTE"]: lambda context, value: context >= value,
  OPERATORS["LT"]: lambda context, value: context < value,
  OPERATORS["IN"]: lambda context, value:
                   context >= value[0] and context < value[1] if value[0] < value[1]
                   else context >= value[0] or context < value[1]
}
