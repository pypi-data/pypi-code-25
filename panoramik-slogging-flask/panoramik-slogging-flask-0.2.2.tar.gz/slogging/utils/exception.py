from traceback import extract_tb

from qualname import qualname


def exception_fmt_by_exc_info(exc_info):
    """
    Format exception
    :param exception: Exception to format
    :type exception Exception
    :return: dict
    """

    exc_type, exception, tb = exc_info

    traceback = [
        {
            'code_text': text,
            'filename': filename,
            'func_name': func_name,
            'line_no': line_no
        } for filename, line_no, func_name, text in extract_tb(tb)
    ] if tb else None

    exc_module_name = exc_type.__module__
    try:
        exc_type_name = qualname(exc_type)
    except AttributeError:
        exc_type_name = exc_type.__name__

    res = {
        'type': exc_module_name + '.' + exc_type_name,
        'message': str(exception),
        'traceback': traceback
    }
    if hasattr(exception, '_slogger_custom'):
        custom = exception._slogger_custom
        if isinstance(custom, dict):
            res['custom'] = exception._slogger_custom

    return res
