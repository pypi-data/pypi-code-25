import os
import sys


def error_message(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()

    return {
        'type': exc_type,
        'file_name': os.path.split(exc_tb.tb_frame.f_code.co_filename)[1],
        'line_number': exc_tb.tb_lineno,
        'message': str(e)
    }
