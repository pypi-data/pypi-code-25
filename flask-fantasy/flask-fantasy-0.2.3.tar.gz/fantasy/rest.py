"""
=============
Rest
=============
"""
from webargs.flaskparser import parser


def pagenation_args(argmap, req=None, locations=None, as_kwargs=False,
                    validate=None):
    """
    ..todo::
        未开发完成

    :param argmap:
    :param req:
    :param locations:
    :param as_kwargs:
    :param validate:
    :return:
    """

    f = parser.user_args(argmap, req=None, locations=None, as_kwargs=False,
                         validate=None)
    return f()
