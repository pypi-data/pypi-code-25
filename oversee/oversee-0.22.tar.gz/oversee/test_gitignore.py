from oversee import gitignore


def test_replace_lines():
    lines = ['<name>  s <name>', 'sa <other>']
    variables = dict(name='test', other='temp')

    assert gitignore.replace_lines(lines, variables) == ['test  s test', 'sa temp']
