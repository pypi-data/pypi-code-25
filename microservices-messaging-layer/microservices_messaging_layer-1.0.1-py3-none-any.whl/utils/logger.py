
import logging
class Logger(object):
    __instance = None
    def __new__(cls):
        if Logger.__instance == None:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            logger.debug('Logger ready, my Lord.')
            Logger.__instance = object.__new__(cls)
            Logger.__instance.logger = logger
        return Logger.__instance


    def logmsg(self,level=None,*args):
        #self.logger.setLevel(logging.WARNING)
        """
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
        """
        if level == 'debug':
            return self.logger.debug(args)
        if level == 'info':
            return self.logger.info(args)
        if level == 'warn':
            return self.logger.warn(args)
        if level == 'error':
            return self.logger.error(args)
        if level == 'critical':
            return self.logger.critical(args)
        else:
            return self.logger.debug(args)
