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

from .metric_value import MetricValue


class PercentileMetricValue(MetricValue):
    """Represents percentile metrics values.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar _count: The number of values for the metric.
    :vartype _count: float
    :ivar average: The average value of the metric.
    :vartype average: float
    :ivar maximum: The max value of the metric.
    :vartype maximum: float
    :ivar minimum: The min value of the metric.
    :vartype minimum: float
    :ivar timestamp: The metric timestamp (ISO-8601 format).
    :vartype timestamp: datetime
    :ivar total: The total value of the metric.
    :vartype total: float
    :ivar p10: The 10th percentile value for the metric.
    :vartype p10: float
    :ivar p25: The 25th percentile value for the metric.
    :vartype p25: float
    :ivar p50: The 50th percentile value for the metric.
    :vartype p50: float
    :ivar p75: The 75th percentile value for the metric.
    :vartype p75: float
    :ivar p90: The 90th percentile value for the metric.
    :vartype p90: float
    :ivar p95: The 95th percentile value for the metric.
    :vartype p95: float
    :ivar p99: The 99th percentile value for the metric.
    :vartype p99: float
    """

    _validation = {
        '_count': {'readonly': True},
        'average': {'readonly': True},
        'maximum': {'readonly': True},
        'minimum': {'readonly': True},
        'timestamp': {'readonly': True},
        'total': {'readonly': True},
        'p10': {'readonly': True},
        'p25': {'readonly': True},
        'p50': {'readonly': True},
        'p75': {'readonly': True},
        'p90': {'readonly': True},
        'p95': {'readonly': True},
        'p99': {'readonly': True},
    }

    _attribute_map = {
        '_count': {'key': '_count', 'type': 'float'},
        'average': {'key': 'average', 'type': 'float'},
        'maximum': {'key': 'maximum', 'type': 'float'},
        'minimum': {'key': 'minimum', 'type': 'float'},
        'timestamp': {'key': 'timestamp', 'type': 'iso-8601'},
        'total': {'key': 'total', 'type': 'float'},
        'p10': {'key': 'P10', 'type': 'float'},
        'p25': {'key': 'P25', 'type': 'float'},
        'p50': {'key': 'P50', 'type': 'float'},
        'p75': {'key': 'P75', 'type': 'float'},
        'p90': {'key': 'P90', 'type': 'float'},
        'p95': {'key': 'P95', 'type': 'float'},
        'p99': {'key': 'P99', 'type': 'float'},
    }

    def __init__(self, **kwargs) -> None:
        super(PercentileMetricValue, self).__init__(**kwargs)
        self.p10 = None
        self.p25 = None
        self.p50 = None
        self.p75 = None
        self.p90 = None
        self.p95 = None
        self.p99 = None
