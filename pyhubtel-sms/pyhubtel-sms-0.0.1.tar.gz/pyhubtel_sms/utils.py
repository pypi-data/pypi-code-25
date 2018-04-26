# -*- coding: utf-8 -*-

import phonenumbers
from dateutil.parser import parse
from .exceptions import InvalidPhoneNumberError, InvalidTimeStringError


def parse_phone_number(phone_number):
    """Parse phone number.

    Args:
        phone_number (str): Phone number. ie. 050xxxxxxx

    Returns:
        str: E164 formatted phone number. ie. +23350xxxxxxx

    Raises:
        InvalidPhoneNumberError: If `phone_number` is not successfully
            parsed as a local (GH) phone number.

    """
    try:
        local_number = phonenumbers.parse(phone_number, "GH")
        if phonenumbers.is_valid_number(local_number):
            e164 = phonenumbers.format_number(
                local_number, phonenumbers.PhoneNumberFormat.E164
            )
            return e164

    except phonenumbers.phonenumberutil.NumberParseException:
        raise InvalidPhoneNumberError(
            "{}: is not a valid phone number.".format(phone_number)
        )


def parse_time(time, drop_seconds=None):
    """Parse time.

    Args:
        time (str): Accepted inputs include:
            * 2018-03-23 10:27:24
            * 2018-03-23T10:27:24.5
            * Fri Mar 23 10:27:24
            * Fri Mar 23 10:27:24 2018
            * 2018 10:27:24 GMT 23 Mar Fri
            * Fri Mar 23 10:27:21 GMT 2018
            * Fri Mar 23
            * 10:27 am

        drop_seconds (bool): Boolean flag to drop seconds from formatted
            time string.

    Returns:
        str: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM

    Raises:
        InvalidTimeStringError: If `time` is not :obj:`str` or not
            successfully parsed.

    """
    try:
        if time:
            datetime_obj = parse(time, fuzzy=True)
            if drop_seconds:
                return datetime_obj.strftime("%Y-%m-%d %H:%M")

            return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    except (ValueError, OverflowError) as e:
        raise InvalidTimeStringError(e)


def prune(body):
    """Removes dictionary keys with value False."""
    return {k: v for (k, v) in body.items() if bool(v) is not False}
