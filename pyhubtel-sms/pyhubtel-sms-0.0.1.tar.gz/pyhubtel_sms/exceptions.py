# -*- coding: utf-8 -*-


def _explain_response(response):
    reasons = {
        400: {
            3: "The message body was too long.",
            4: "The message is not routable on the Hubtel gateway.",
            6: "The message content was rejected or is invalid.",
            7: "One or more parameters are not allowed in the message.",
            8: "One or more parameters are not valid for the message.",
        },
        402: "Your account does not have enough messaging credits to send "
        "the message.",
        403: "Recipient has not given his/her approval to receive messages.",
        404: "The specified message was not found.",
    }

    sub_code = response.json().get("Status", False)

    try:
        return reasons.get(response.status_code).get(sub_code, None)

    except (AttributeError, KeyError):
        return reasons.get(response.status_code, None)


class HubtelAPIException(Exception):

    """An ambiguous exception occurred."""

    def __init__(self, *args):
        super(HubtelAPIException, self).__init__(*args)

        if len(self.args) == 0:
            self.reason = ""
        if len(self.args) == 1:
            self.reason = str(self.args[0])
        if len(self.args) == 2:
            error_message = self.args[0]
            response = self.args[1]
            reason = _explain_response(response)
            self.reason = str("{}: {}".format(error_message, reason))
        if len(self.args) >= 3:
            self.reason = str(self.args)

    def __str__(self):
        if len(self.args) == 0:
            return ""

        if self.reason:
            return str(self.reason)

        return str(self.args)


class SMSError(HubtelAPIException):
    """An SMS error occurred."""


class InvalidPhoneNumberError(HubtelAPIException):
    """An invalid phone number error occurred."""


class InvalidTimeStringError(HubtelAPIException):
    """An invalid time string error occured."""


class InvalidMessageError(HubtelAPIException):
    """An invalid message error occurred."""
