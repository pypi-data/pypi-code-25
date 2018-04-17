# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class ApiError(Model):
    """Api error.

    :param details: The Api error details
    :type details: list[~azure.mgmt.compute.v2015_06_15.models.ApiErrorBase]
    :param innererror: The Api inner error
    :type innererror: ~azure.mgmt.compute.v2015_06_15.models.InnerError
    :param code: The error code.
    :type code: str
    :param target: The target of the particular error.
    :type target: str
    :param message: The error message.
    :type message: str
    """

    _attribute_map = {
        'details': {'key': 'details', 'type': '[ApiErrorBase]'},
        'innererror': {'key': 'innererror', 'type': 'InnerError'},
        'code': {'key': 'code', 'type': 'str'},
        'target': {'key': 'target', 'type': 'str'},
        'message': {'key': 'message', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(ApiError, self).__init__(**kwargs)
        self.details = kwargs.get('details', None)
        self.innererror = kwargs.get('innererror', None)
        self.code = kwargs.get('code', None)
        self.target = kwargs.get('target', None)
        self.message = kwargs.get('message', None)
