from yangsutil.string_util import StringUtil


class DictUtil:
    @staticmethod
    def dict_list_to_dict(dict_list, order_key=None):
        result_dict = dict()

        for dict_item in dict_list:

            for item_key in dict_item.keys():

                data = dict_item[item_key]

                try:
                    if type(data) == dict:
                        result_dict[item_key].append(data)
                    else:
                        result_dict[item_key] += dict_item[item_key]
                except KeyError:
                    if type(data) == dict:
                        result_dict[item_key] = [data]
                    elif type(data) == list:
                        result_dict[item_key] = list(data)
                    else:
                        result_dict[item_key] = data

        if order_key is not None:
            for result_dict_key in result_dict.keys():
                result_dict[result_dict_key].sort(key=lambda x: x[order_key])

        return result_dict

    @staticmethod
    def is_avail_key(dict_obj, key):

        try:
            tmp = dict_obj[key]
        except KeyError:
            return False

        if type(tmp) == str:
            return not StringUtil.is_none(tmp)
        else:
            return True
