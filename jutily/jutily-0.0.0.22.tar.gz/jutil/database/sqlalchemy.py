from sqlalchemy import and_, or_


def filter_dict(model_class, parameter_dict):
    filter_parameter_dict = {}
    for key, value in parameter_dict.items():
        filter_parameter_dict['model_class.{}'.format(key)] = value
    return filter_parameter_dict


def filter_string_junction(model_class, parameter_dict, junction_string, expression):
    """
    CHANGELOG

    CHanged 19.04.2018
    Replacing a double quote with a single quote whenever dealing with a string value because when the string value
    e.g. a title contains a double quote naturally that lead to an error
    :param model_class:
    :param parameter_dict:
    :param junction_string:
    :param expression:
    :return:
    """
    filter_parameter_dict = filter_dict(model_class, parameter_dict)
    string_list = [junction_string, '(']
    for key, value in filter_parameter_dict.items():
        try:
            value_string = '{}'.format(int(value))
        except:
            value_string = '"{}"'.format(value.replace('"', "'"))
        expression_string = expression.format(key, value_string)
        string_list.append(expression_string)
        string_list.append(',')
    string_list[-1] = ')'
    filter_string = ''.join(string_list)
    return filter_string


def filter_string_and(model_class, parameter_dict, expression='{}=={}'):
    return filter_string_junction(
        model_class,
        parameter_dict,
        'and_',
        expression
    )


def filter_string_or(model_class, parameter_dict, expression='{}=={}'):
    return filter_string_junction(
        model_class,
        parameter_dict,
        'or_',
        expression
    )


def get_or_create(model_class, parameter_dict):
    # Attempting to get the model from the database
    filter_string = filter_string_and(model_class, parameter_dict)
    a = model_class.query.filter(eval(filter_string)).first()
    if a is not None:
        return a
    b = model_class(**parameter_dict)
    return b


def add_elements(list_attribute, model_list):
    for model in model_list:
        list_attribute.append(model)