from logging import getLogger
from logging.config import dictConfig
from nrask.options import define,options
from tornado.process import task_id

__all__ = ['Raven']

class Raven(object):
    __logger = None
    __name = None

    @property
    def __formatter__(self):
        try:
            assert options.raven_color
        except AssertionError:
            return {
                'format':options.raven_no_color_fmt
            }
        except:
            raise
        return {
            '()':'colorlog.ColoredFormatter',
            'format':options.raven_color_fmt
        }

    @property
    def logger(self):
        try:
            assert self.__logger
        except AssertionError:
            self.__config__()
            self.__logger = getLogger(self.__name)
        except:
            raise
        return self.__logger

    def __config__(self):
        dictConfig({
            'disable_existing_loggers':False,
            'formatters':{
                'nrask':self.__formatter__
            },
            'handlers':{
                'default':{
                    'level':str(options.logging).upper(),
                    'class':'logging.StreamHandler',
                    "formatter": "nrask"
                }
            },
            'loggers':{
                '': {
                    'handlers': ['default'],
                    'level':str(options.logging).upper(),
                    'propagate':True
                }
            },
            'version':1
        })
        return True

    def __init__(self,name='nrask'):
        self.__name = name

    def critical(self,arg):
        self.logger.critical(arg)
        return True

    def debug(self,arg):
        self.logger.debug(arg)
        return True

    def error(self,arg):
        self.logger.error(arg)
        return True

    def info(self,arg):
        self.logger.info(arg)
        return True

    def mark(self,_):
        return '[%s]> %s' % (task_id(),_)

    def warning(self,arg):
        self.logger.warning(arg)
        return True
