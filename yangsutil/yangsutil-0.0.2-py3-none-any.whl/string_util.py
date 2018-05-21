class StringUtil:
    @staticmethod
    def is_empty_string(string):
        return string is None or string == ''

    @staticmethod
    def comma_string_to_list(string):
        return [str(item).rstrip().lstrip() for item in string.split(',') if item != '']

    @staticmethod
    def list_to_comma_string(list_item):
        data = ''
        for item in list_item:
            data += '%s,' % item

        return data[:len(data) - 1]

    @staticmethod
    def number_expression(number):
        if type(number) is str:

            try:
                tmp_number = int(number)
            except ValueError:

                try:
                    tmp_number = float(number)
                except ValueError:
                    tmp_number = None

        else:
            tmp_number = number

        if tmp_number is None:
            return None

        return str("{:,}".format(tmp_number))

    @staticmethod
    def blank_to_underscore(plain, is_lower=False):
        target = plain.lower() if is_lower is True else plain

        tmp = ''
        for word in target.split(' '):
            tmp += word + '_'

        return tmp[:len(tmp) - 1]
