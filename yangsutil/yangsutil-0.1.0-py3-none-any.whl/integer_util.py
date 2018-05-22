class IntegerUtil:

    NORMAL = 0
    POSITIVE = 1
    NEGATIVE = 2
    POSITIVE_WITHOUT_ZERO = 3
    NEGATIVE_WITHOUT_ZERO = 4

    @staticmethod
    def is_check(string, number_type=0):

        try:
            tmp = int(string)
        except (TypeError, ValueError):
            return False

        if number_type == IntegerUtil.POSITIVE:
            if tmp < 0:
                return False

        elif number_type == IntegerUtil.NEGATIVE:
            if tmp > 0:
                return False

        elif number_type == IntegerUtil.POSITIVE_WITHOUT_ZERO:
            if tmp <= 0:
                return False

        elif number_type == IntegerUtil.NEGATIVE_WITHOUT_ZERO:
            if tmp >= 0:
                return False

        return True
