import os
from logging import StreamHandler, Handler, getLevelName

import six
from structlog import BoundLoggerBase


class SemanticLogger(BoundLoggerBase):
    def msg(self, event, **kw):
        if "status" not in kw:
            return self._proxy_to_logger("msg", event, status="ok", **kw)
        else:
            return self._proxy_to_logger("msg", event, **kw)

    def info(self, event=None, **kw):
        """
        Process event and call :meth:`logging.Logger.info` with the result.
        """
        return self._proxy_to_logger("info", event, **kw)

    def user_error(self, event, **kw):
        self.msg(event, status="user_error", **kw)

    def _process_event(self, method_name, event, event_kw):
        """
        Combines creates an `event_dict` and runs the chain.

        Call it to combine your *event* and *context* into an event_dict and
        process using the processor chain.

        :param str method_name: The name of the logger method.  Is passed into
            the processors.
        :param event: The event -- usually the first positional argument to a
            logger.
        :param event_kw: Additional event keywords.  For example if someone
            calls ``log.msg("foo", bar=42)``, *event* would to be ``"foo"``
            and *event_kw* ``{"bar": 42}``.
        :raises: :class:`structlog.DropEvent` if log entry should be dropped.
        :raises: :class:`ValueError` if the final processor doesn't return a
            string, tuple, or a dict.
        :rtype: `tuple` of `(*args, **kw)`

        .. note::

            Despite underscore available to custom wrapper classes.

            See also :doc:`custom-wrappers`.

        .. versionchanged:: 14.0.0
            Allow final processor to return a `dict`.
        """
        event_dict = self._context.copy()
        event_dict.update(**event_kw)
        if event is not None:
            event_dict["event"] = event
        for proc in self._processors:
            event_dict = proc(self._logger, method_name, event_dict)

        if (isinstance(event_dict, six.string_types)) \
                or (isinstance(event_dict, bytes) and six.PY3):
            return (event_dict,), {}
        elif isinstance(event_dict, tuple):
            # In this case we assume that the last processor returned a tuple
            # of ``(args, kwargs)`` and pass it right through.
            return event_dict
        elif isinstance(event_dict, dict):
            return (), event_dict
        else:
            raise ValueError(
                "Last processor didn't return an approriate value.  Allowed "
                "return values are a dict, a tuple of (args, kwargs), or a "
                "string."
            )


class FileHandler(StreamHandler):
    """
    A handler class which writes formatted logging records to disk files.
    """

    def __init__(self, filename='file_.log', mode='a', encoding=None, delay=False):
        """
        Open the specified file and use it as the stream for logging.
        """
        from iohandler import IOFile
        self.fph = IOFile.IOFileHandler()
        self.filename = filename
        filename = os.fspath(filename)
        self.baseFilename = os.path.abspath(filename)
        fn = os.path.basename(self.filename)
        self._file_object = self.fph.open(file_name=fn,
                                          file_path=os.path.dirname(filename),
                                          create_file_if_none=True, mode='ab+')
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            # We don't open the stream, but we still need to call the
            # Handler constructor to set level, formatter, lock etc.
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())

    def close(self):
        """
        Closes the stream.
        """
        self.acquire()
        try:
            try:
                if self.stream:
                    try:
                        self.flush()
                    finally:
                        stream = self.stream
                        self.stream = None
                        if hasattr(stream, "close"):
                            stream.close()
            finally:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay is set
                StreamHandler.close(self)
        finally:
            self.release()

    def _open(self):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.
        """
        try:
            return open(self.baseFilename, self.mode, encoding=self.encoding)
        except ValueError:
            # "ValueError: binary mode doesn't take an encoding argument"
            return open(self.baseFilename, self.mode)

    def emit(self, record):
        """
        Emit a record.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        if self.stream is None:
            self.stream = self._open()
        try:
            msg = record.msg
            self.fph.write(file_object=self._file_object, data=msg)
        except UnicodeDecodeError:
            record.msg = {"log": "a"}
            self.emit(record)
        except UnicodeEncodeError:
            record.msg = {"log": "b"}
            self.emit(record)
            # if self.stream is None:
            #     self.stream = self._open()
            # StreamHandler.emit(self, record)

    def __repr__(self):
        level = getLevelName(self.level)
        return '<%s %s (%s)>' % (self.__class__.__name__, self.baseFilename, level)

# log = structlog.wrap_logger(structlog.PrintLogger(), wrapper_class=SemanticLogger)
# log = log.bind(user="fprefect")
# log.user_error("user.forgot_towel")
