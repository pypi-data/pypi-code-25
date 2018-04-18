__author__ = 'Bohdan Mushkevych'

from antlr4 import ParserRuleContext
from grammar.sdplLexer import sdplLexer


def print_comments():
    """ prints SDPL comments into the output stream
        NOTICE: comment delimiter is taken as `self.COMMENT_DELIMITER`
    """

    def _print_comments(method):
        def wrapper(self, ctx:ParserRuleContext):
            assert hasattr(self, 'output_stream'), \
                'print_comments decorator applied to method {0}.{1}: missing required method {0}.output_stream'.\
                format(self.__class__.__name__, method.__name__)

            assert hasattr(self, 'token_stream'), \
                'print_comments decorator applied to method {0}.{1}: missing required method {0}.token_stream'.\
                format(self.__class__.__name__, method.__name__)

            cmt_channel = self.token_stream.getHiddenTokensToLeft(ctx.start.tokenIndex, sdplLexer.CHANNEL_COMMENTS)
            if cmt_channel:
                for comment in cmt_channel:
                    self.output_stream.write('{0} {1}'.format(self.COMMENT_DELIMITER, comment.text))

            return method(self, ctx)

        return wrapper
    return _print_comments
