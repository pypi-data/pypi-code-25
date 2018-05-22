import re


def get_sass_variables(contents):
    variables = {}
    regex = r'\$([^:]+):[ ]*([^;]+);?;'

    for pair in re.findall(regex, contents):
        variables[pair[0]] = pair[1]

    return variables
