def generate_parameters(parameters, operators):
    return ['{}[{}]'.format(parameter, operator)
            for parameter in parameters
            for operator in operators]


def generate_sorting_parameters(parameters):
    return generate_parameters(parameters, ['asc', 'desc'])


def generate_date_parameters(parameters):
    return generate_parameters(parameters, ['after', 'before', 'on', 'between'])


def generate_equals_parameters(parameters):
    return generate_parameters(parameters, ['is', 'is_not'])


def generate_collection_parameters(parameters):
    return generate_parameters(parameters, ['in', 'not_in'])


def generate_comparison_parameters(parameters):
    return generate_parameters(parameters, ['lt', 'lte', 'gt', 'gte'])
