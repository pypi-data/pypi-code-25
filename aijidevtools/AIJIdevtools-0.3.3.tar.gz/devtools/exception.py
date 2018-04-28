def mute(cond, default=None):
    def dec(func):
        if cond:
            def f(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    return default
            return f

        else:
            return func
    return dec
