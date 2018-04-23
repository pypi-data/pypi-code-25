import inspect


class DustExec:

    @staticmethod
    def exec(string, params, error_handler):
        exec(string, globals())
        main = globals().get('dust_main', None)
        if not main:
            error_handler('没有找到 dust_main 入口')
            return None
        return main(*params)


