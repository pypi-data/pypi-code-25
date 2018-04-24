from inspect import getcallargs, getargspec

def ensure_params_under_instance_context(func):
    argspecs = getargspec(func)

    def wrapper(*args, **kwargs):
        combined_kwargs = {key: val for (key, val) in args[0].__dict__.items()
                           if key in argspecs.args}
        combined_kwargs.update(kwargs)
        getcallargs(func, *args, **combined_kwargs)
        return func(*args, **combined_kwargs)
    return wrapper

def ensure_params_under_instance_context_dict(*dict_names):
    def decorator(func):
        def wrapper(*args, **kwargs):
            combined_kwargs = {}
            for name in dict_names:
                combined_kwargs.update(getattr(args[0], name, {}))
            getcallargs(func, *args, **combined_kwargs)
            return func(*args, **combined_kwargs)
        return wrapper
    return decorator

if __name__ == '__main__':
    class Test(object):

        def __init__(self):
            self.a = 1
            self.b = 2
            self.context = {
                'a': 3,
                'b': 4,
            }

        @ensure_params_under_instance_context
        def f_1(self, a, b, c=1):
            print(a, b, c)

        @ensure_params_under_instance_context_dict('context')
        def f_2(self, a, b, c=1):
            print(a, b, c)

    test = Test()
    test.f_1()
    test.f_2()
