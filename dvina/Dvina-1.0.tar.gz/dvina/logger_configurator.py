import logging.config


class LoggerConfigurator(object):
    @staticmethod
    def configure_logging(dict_config=None):
        """
        This static function configures logging ro the library using :func:`dictConfig` method 
        of python ``logging.config`` module. 
        Every class of the library gets loggers using ``self._logger = logging.getLogger(__name__)``, thus 
        you will need to configure logger ``'root'`` in order for the settings to be propagated to the loggers 
        down the hierarchy.
        If no config is passed, NullHandler is used to avoid logger configuration warnings
          
        Parameters
        ----------
        dict_config : dict, optional
            dictionary for configuring root logger
            
        Examples
        --------
        Here is an example of how you can configure logging
        :: 
        
            from dvina import LoggerConfigurator
            dict_config = {
                    'version': 1,
                    'handlers': {
                        'console': {
                            'class': 'logging.StreamHandler',
                        }
                    },
                    'root': {
                        'level': 'WARNING',
                        'handlers': ['console']
                    },
                }
            LoggerConfigurator.configure_logging(dict_config)
                    
        """
        if dict_config is not None:
            logging.config.dictConfig(dict_config)
