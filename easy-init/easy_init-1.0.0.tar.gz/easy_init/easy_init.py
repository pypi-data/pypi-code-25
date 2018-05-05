def _generate_init(nondefaultablefields, defaultablefields):
    nondefaultablefields = list(nondefaultablefields)
    return '''def __init__({}):{}'''.format(', '.join(['self'] + nondefaultablefields + ['{}={}'.format(k,v) for k,v in defaultablefields.items()]),
                                            ''.join(['\n    self.{} = {}'.format(k, k) for k in nondefaultablefields]) + ''.join(['\n    self.{} = {}'.format(k, k) for k in defaultablefields]) if nondefaultablefields or defaultablefields else '\n    pass')

#note: if defaults are not primitive data types, use a string of the code to execute
def init(*nondefaultablefields, **defaultablefields):
    def decorate(cls):
        exec(_generate_init(nondefaultablefields, defaultablefields), globals(), locals())
        cls.__init__ = locals()['__init__']
        return cls
    return decorate


if __name__ == '__main__':
    print('using @init to create initializer example...')

    @init('r', 'g', 'b', a=1.0)
    class Color:
        def __str__(self):
            return 'Color({}, {}, {}, {})'.format(self.r, self.g, self.b, self.a)

    print(Color(1, 2, 3))

    print('@init empty example...')
    @init()
    class Nothing:
        def __str__(self):
            return 'Nothing()'

    print(Nothing())

    print('now that class should throw error if trying to pass anything in:')
    try:
        Nothing(5)
    except TypeError as e:
        print(e)
    print('or a default:')
    try:
        Nothing(p=7)
    except TypeError as e:
        print(e)

    print('back to Color class, sending not enough args:')
    try:
        print(Color(3,4))
    except TypeError as e:
        print(e)
