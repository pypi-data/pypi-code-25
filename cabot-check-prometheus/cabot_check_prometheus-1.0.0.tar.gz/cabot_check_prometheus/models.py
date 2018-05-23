import datetime
import socket
import ssl
import requests

from django.db import models

from cabot.cabotapp.models import StatusCheck, StatusCheckResult

def process_matrix(data):
    metrics = []
    values = []
    for result in data['result']:
        metrics.append(result['metric'])
        metricValues = []
        for value in result['value']:
            metricValues.append(value)
        values.append(metricValues)
    if len(data) > 0:
        raise Exception("Metrics failed: {}\nWith values: {}".format(str(metrics), str(values)))


def process_vector(data):
    metrics = []
    values = []
    for result in data['result']:
        metrics.append(result['metric'])
        metricValues = []
        for value in result['value']:
            metricValues.append(value)
        values.append(metricValues)
    if len(data) > 0:
        raise Exception("Metrics failed: {}\nWith values: {}".format(str(metrics), str(values)))


def process_scalar(data):
    value = [data]
    if len(data) > 0:
        raise Exception("Metrics failed with values: " + str(value))


def process_string(data):
    value = [data]
    if len(data) > 0:
        raise Exception("Metrics failed with values: {}".format(str(value)))


def process_unknown(data):
    print('processing unknown')

class PrometheusStatusCheck(StatusCheck):
    check_name = 'prometheus'
    edit_url_name = 'update-prometheus-check'
    duplicate_url_name = 'duplicate-prometheus-check'
    icon_class = 'glyphicon-fire'
    host = models.TextField(
        help_text='Host to check.',
    )
    query = models.TextField(
        help_text='Query to execute.',
    )

    def _run(self):
        result = StatusCheckResult(status_check=self)

        try:
            payload = {
                'query': 'rate(apiserver_request_count{code=~"^(?:5..)$"}[5m]) / rate(apiserver_request_count[5m]) * 100 > 2'
            }
            r = requests.get("http://prometheus.widen-prod.com/api/v1/query", params=payload)
            data = r.json()['data']
            type = data['resultType']
            if type == 'matrix':
                process_matrix(data)
            elif type == 'vector':
                process_vector(data)
            elif type == 'scalar':
                process_scalar(data)
            elif type == 'string':
                process_string(data)
            else:
                process_unknown(data)
        except Exception as e:
            result.error = u"{} {} {}".format(e.message, self.host, self.port)
            result.succeeded = False
        else:
            result.succeeded = True

        return result