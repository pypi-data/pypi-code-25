from rook.interface import Rook

def wrapper(f):
    def handler(event, context):
        ret = f(event, context)
        Rook().flush()
        return ret

    from rook import auto_start
    return handler