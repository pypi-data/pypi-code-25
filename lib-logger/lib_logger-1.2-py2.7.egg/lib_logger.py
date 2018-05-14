
import os, sys
import logging
import multiprocessing

###############################################################

###############################################################

#
#   Add per module logging capability
#
#



class logger:

    __initialized = False
    __log_identifier = 'log_'
    __log_file_append = True
    __log_file_level = 'info'
    __log_filename = ''
    __level_list = ['debug', 'info', 'warning', 'error']
    __level = 'warning'
    __logger_dict = {}
    __logger_level_dict = {}


    def __init__(self, log_id='log_', log_file_level='info', log_file='', log_file_append=True, level_dict=None, level='warning', multiprocess_flag=False):

        # recover caller module name and id
        frame = sys._getframe(1)
        module = frame.f_code.co_filename
        module_id = self.__log_identifier + os.path.splitext(os.path.split(module)[1])[0]
        try: level_dict[module_id] = level
        except: level_dict = {module_id: level}

        if not self.__initialized:
            self.__log_identifier = log_id
            self.__log_file_level = log_file_level
            self.__log_file_append = log_file_append
            self.__log_filename = self._file_log(log_file)
            self._logger_init()
            self.__level = level
            self.__initialized = True
            self._multiprocess_flag = multiprocess_flag

        self._logger_init_level(level_dict)
        self._module_logger(level_dict)
        return



    #
    # Use the filename and create it in the user_folder/autoLog/name.log
    # user_folder:  user's Windows folder
    #
    def _file_log(self, log_file):

        logFolder = '/Documents/testAutoLog/'
        logPathFolder = os.path.expanduser('~') + logFolder
        if  not os.path.isdir(os.path.dirname(logPathFolder)):
            os.makedirs(os.path.dirname(logPathFolder))

        # Create the folder if it does not exist
        if log_file == '':
            log_file = 'autoLog'
        logPathName = logPathFolder + os.path.splitext(os.path.basename(log_file))[0] + '.log'
        return logPathName



    # Initialize internal variables
    #
    def _logger_init(self):

        self.__log_file_append = True
        self.__log_file_level = self._formatted_level(self.__log_file_level)
        if self.__log_filename !='':
            if not self.__log_file_append:
                filemode = 'w'
                log_append = False
                # delete pre-existing file
                try:
                    os.remove(self.__log_filename)
                except OSError:
                    pass
            else:
                filemode = 'a'
            FORMAT_BASE = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            logging.basicConfig(level=self.__log_file_level, filename=self.__log_filename, filemode=filemode, format=FORMAT_BASE)

        return

    # Set initial module log levels
    # A dictionary with the log module id as keys and value as either Boolean or log level string
    # If value is boolean then the default level is used
    #
    def _logger_init_level(self, level_dict):

        for module_id in level_dict.keys():
            try:
                level = self.__logger_level_dict[module_id]
                if self.__initialized:
                    continue
                pass
            except: pass

            if self.__log_identifier not in str(module_id): continue
            if level_dict[module_id] not in self.__level_list:
                self.__logger_level_dict[module_id] = self.__level
            else: self.__logger_level_dict[module_id] = level_dict[module_id]
        return


    def _module_logger(self, level_dict):

        for module_id in level_dict.keys():
            try:
                level = self.__logger_level_dict[module_id]
                if self.__initialized:
                    continue
                pass
            except:
                pass

            self._log_module_init(module_id)

        return


    #   This function return the corresponding "logging" package level
    #   Default log level = WARNING
    #
    def _set_logger_level(self, module_id):

        try: level = self.__logger_level_dict[module_id]
        except:
            self.__logger_level_dict[module_id] = self.__level
            level = self.__level

        module_list = self.__logger_level_dict.keys()
        if module_id not in module_list: return logging.WARNING
        try:
            lower_level = level.lower()
        except:
            return logging.WARNING
        if lower_level not in self.__level_list:
            return logging.WARNING

        fomat_level = self._formatted_level(level)

        return fomat_level


    def _formatted_level(self, level):
        if level.lower() == 'debug':    return logging.DEBUG
        if level.lower() == 'info':     return logging.INFO
        if level.lower() == 'error':    return logging.ERROR
        if level.lower() == 'critical': return logging.CRITICAL
        if level.lower() == 'fatal':    return logging.FATAL
        return logging.WARNING



    def _log_module_init(self, module_id):

        FORMAT_BASE = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

        # Console
        console = logging.StreamHandler()
        # Console log output formatting
        formatter = logging.Formatter(FORMAT_BASE)
        console.setFormatter(formatter)

        # Logger
        if self._multiprocess_flag:
            logger = multiprocessing.log_to_stderr()
        else:
            module_name = module_id.replace(self.__log_identifier, '')
            logger = logging.getLogger(module_name)

        logger.addHandler(console)
        logger.setLevel(self._set_logger_level(module_id))

        self.__logger_dict[module_id] = logger

        return logger


    #
    #   cr=True     A CR is inserted after the stack frame display
    #               Default: False
    #   depth       This indicates the depth of the stack frame to be shown.
    #               -1 indicates maximum depth.
    #               None indicates no stack frame
    #               Default: -1
    #
    def log(self, level, msg, cr=False, depth=-1):

        # recover caller module name and id
        frame = sys._getframe(1)
        module = frame.f_code.co_filename
        module_id = self.__log_identifier + os.path.splitext(os.path.split(module)[1])[0]

        try: logger = self.__logger_dict[module_id]
        except:
            logger = self._log_module_init(module_id)

        if depth != None:
            msg = self._stack_frame(remove='log', depth=depth, cr=cr) + msg

        if level == 'debug':
            logger.debug(msg)
        elif level == 'info':
            logger.info(msg)
        elif level == 'warning':
            logger.warning(msg)
        elif level == 'error':
            logger.error(msg)
        elif level == 'critical':
            logger.critical(msg)
        elif level == 'fatal':
            logger.fatal(msg)

        return




    ############################################################
    #
    #       Return stack frame up to 'depth' level down to be
    #       optionally displayed
    #       Can be used for logging.
    #
    #   i.e.: nested calls ==> stackFrame = call1::call2::call3::call4::
    #
    ############################################################

    def _stack_frame(self, depth=-1, remove=None, cr=False):
        stackFrame = ''
        num = 0

        while True:

            if depth == 0:
                break
            frame = sys._getframe(num)
            # Find starting level
            method_name  = frame.f_code.co_name
            if method_name == '<module>' or method_name == 'run':
                lineno = frame.f_lineno
                launchFile = os.path.splitext(os.path.basename(frame.f_code.co_filename))[0]
                stackFrame = '%s(%d)::' % (launchFile, lineno) + stackFrame
                break
            if frame.f_code.co_name != '_stack_frame' and frame.f_code.co_name != remove:
                lineno = frame.f_lineno
                stackFrame = frame.f_code.co_name + '(%d)::' % lineno + stackFrame
                depth -= 1
            num += 1

        stackFrame = '[' + stackFrame + ']'
        stackFrame += ' '
        if cr:
            stackFrame += '\n   '
        return stackFrame

