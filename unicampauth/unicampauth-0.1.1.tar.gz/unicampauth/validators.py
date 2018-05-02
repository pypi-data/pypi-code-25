import re


class BaseValidator():
    validator = re.compile("")

    def validate_email(self, email):
        return self.validator.match(email.lower()) is not None

    def validate(self, data):
        return self.validate_email(data['email'])


class GUnicampValidator(BaseValidator):
    validator = re.compile("^[a-z]([0-9]{5,7})@g.unicamp.br$")
