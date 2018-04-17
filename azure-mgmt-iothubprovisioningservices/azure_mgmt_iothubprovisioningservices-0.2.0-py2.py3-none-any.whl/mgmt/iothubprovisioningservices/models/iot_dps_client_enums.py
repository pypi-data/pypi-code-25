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

from enum import Enum


class IotDpsSku(str, Enum):

    s1 = "S1"


class State(str, Enum):

    activating = "Activating"
    active = "Active"
    deleting = "Deleting"
    deleted = "Deleted"
    activation_failed = "ActivationFailed"
    deletion_failed = "DeletionFailed"
    transitioning = "Transitioning"
    suspending = "Suspending"
    suspended = "Suspended"
    resuming = "Resuming"
    failing_over = "FailingOver"
    failover_failed = "FailoverFailed"


class AllocationPolicy(str, Enum):

    hashed = "Hashed"
    geo_latency = "GeoLatency"
    static = "Static"


class AccessRightsDescription(str, Enum):

    service_config = "ServiceConfig"
    enrollment_read = "EnrollmentRead"
    enrollment_write = "EnrollmentWrite"
    device_connect = "DeviceConnect"
    registration_status_read = "RegistrationStatusRead"
    registration_status_write = "RegistrationStatusWrite"


class NameUnavailabilityReason(str, Enum):

    invalid = "Invalid"
    already_exists = "AlreadyExists"


class CertificatePurpose(str, Enum):

    client_authentication = "clientAuthentication"
    server_authentication = "serverAuthentication"
