class DatalakeException(Exception):
    pass


class DatasetNotFoundException(DatalakeException):
    pass


class PackageNotFoundException(DatalakeException):
    pass


class InvalidPayloadException(DatalakeException):
    pass


class S3FileDoesNotExist(DatalakeException):
    pass


class DownloadDestinationNotValid(DatalakeException):
    """
    Raised when a download destination is not a directory
    """
    pass


class DownloadFailed(DatalakeException):
    pass
