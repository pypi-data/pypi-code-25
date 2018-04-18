# -*- encoding: utf-8 -*-
class MissingPackageError(Exception):
    error_message = 'mandatory package \'{name}\' not found'

    def __init__(self, package_name):
        self.package_name = package_name
        super(MissingPackageError, self).__init__(
            self.error_message.format(name=package_name))


class IncorrectPackageVersionError(Exception):
    error_message = '\'{name} {installed_version}\' version mismatch ({operation}{required_version})'

    def __init__(self, package_name, installed_version, operation,
                 required_version):
        self.package_name = package_name
        self.installed_version = installed_version
        self.operation = operation
        self.required_version = required_version
        message = self.error_message.format(name=package_name,
                                            installed_version=installed_version,
                                            operation=operation,
                                            required_version=required_version)
        super(IncorrectPackageVersionError, self).__init__(message)


###########################################
###########################################


class InvalidConfigError(Exception):
    error_message = 'Config \'{name}={value}\' invalid'

    def __init__(self, conf_name, conf_value):
        self.conf_name = conf_name
        self.conf_value = conf_value
        message = self.error_message.format(name=conf_name,
                                            value=conf_value)
        super(InvalidConfigError, self).__init__(message)


class MismatchColumnNumberError(Exception):
    error_message = 'Config #columns=\'{num_conf_col}\' and Data #columns=\'{num_data_col}\' mismatched'

    def __init__(self, num_data_col, num_conf_col):
        self.num_data_col = num_data_col
        self.num_conf_col = num_conf_col
        message = self.error_message.format(num_conf_col=num_conf_col,
                                            num_data_col=num_data_col,)
        super(MismatchColumnNumberError, self).__init__(message)


###########################################
###########################################


class MissingConfigTypeError(Exception):
    error_message = 'config type \'{name}\' with value \'{value}\' not found'

    def __init__(self, type_name, type_value):
        self.type_name = type_name
        self.type_value = type_value
        super(MissingConfigTypeError, self).__init__(
            self.error_message.format(name=type_name, value=type_value))
