from StringIO import StringIO


def format_failure(failure):
    """
    get formatted failure
    :param failure: An instance of a twisted failure
    """

    tb_txt = StringIO()
    failure.printTraceback(tb_txt)
    return tb_txt.getvalue()
