import click


def validate(required, unless):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not kwargs[required] and not kwargs[unless]:
                raise ValueError('{} required if {} is not given!'.format(required, unless))
            func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


def list_options(iterable):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ls = kwargs['ls']
            if ls:
                click.echo('\n'.join(iterable))
                return

            for arg in required:
                if not kwargs[arg.name] and not kwargs['ls']:
                    raise ValueError('{} required if {} is not given!'.format(arg.name, 'ls'))

            del kwargs['ls']
            func(*args, **kwargs)

        func = click.option('-ls', is_flag=True, help='Show the options!')(func)

        required = []
        for param in func.__click_params__:
            if isinstance(param, click.Argument):
                if not param.required:
                    continue

                required.append(param)
                param.required = False

        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        wrapper.__click_params__ = func.__click_params__
        return wrapper
    return decorator
