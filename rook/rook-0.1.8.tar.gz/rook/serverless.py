from rook.interface import Rook


# To use:
# @serverless_rook
# def lambda_thingy(event, context):
#     print("hello")
# or
# def lambda_thingy(event, context):
#     print("hello")
# lambda_function = serverless_rook(lambda_thingy)
def serverless_rook(f):
    def handler(event, context):
        from rook import auto_start
        ret = f(event, context)
        Rook().flush()
        return ret

    return handler