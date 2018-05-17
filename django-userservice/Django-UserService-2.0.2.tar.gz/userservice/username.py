from django.conf import settings


def _get_format():
    return getattr(settings, "REMOTE_USER_FORMAT", "eppn")


def expect_uid():
    username_format = _get_format()
    return username_format is not None and\
        (username_format == "uid" or username_format == "uwnetid")


def get_uid(username):
    if username is not None and len(username) and expect_uid():
        try:
            (username, domain) = username.split('@', 1)
        except ValueError as ex:
            pass
    return username
