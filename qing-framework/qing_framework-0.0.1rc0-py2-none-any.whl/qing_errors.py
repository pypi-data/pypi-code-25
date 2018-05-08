class QingError(BaseException):
    pass

class WaitError(QingError):
    pass

class BootError(QingError):
    pass

class ReadingError(QingError):
    pass

class ProcessingError(QingError):
    pass

class WritingError(QingError):
    pass

