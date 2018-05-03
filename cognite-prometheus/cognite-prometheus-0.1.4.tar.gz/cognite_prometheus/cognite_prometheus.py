from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway
from prometheus_client.exposition import basic_auth_handler


def auth_handler(url, method, timeout, headers, data):
    username = CognitePrometheus.username
    password = CognitePrometheus.password
    return basic_auth_handler(
        url,
        method,
        timeout,
        headers,
        data,
        username,
        password
    )


class CognitePrometheus:

    registry = CollectorRegistry()
    prometheus_job = None
    username = None
    password = None
    prometheus_singleton = None

    def __init__(self, job_name: str, username: str, password: str, unconfigured_dummy: bool = False):

        # Allow creating a dummy version of the class
        self.unconfigured_dummy = unconfigured_dummy
        if unconfigured_dummy:
            return

        # Make sure there's only one instance of the class
        if CognitePrometheus.prometheus_singleton:
            raise Exception("Prometheus is a singleton")

        CognitePrometheus.prometheus_job = job_name
        CognitePrometheus.username = username
        CognitePrometheus.password = password
        CognitePrometheus.prometheus_singleton = self

    @staticmethod
    def get_prometheus_object():
        """
        Getter for the Prometheus class' instance. Will return the real object or the dummy, depending on what was
        configured.
        :return:
        """
        if not CognitePrometheus.prometheus_singleton:
            return CognitePrometheus(None, None, None, unconfigured_dummy=True)
        return CognitePrometheus.prometheus_singleton

    def push_to_server(self):
        """
        Will push data to our cognite_prometheus server (if not configured as a dummy).
        :return:
        """
        if self.unconfigured_dummy:
            return
        url = "https://prometheus-push.cognite.ai"
        pushadd_to_gateway(
            url,
            job=CognitePrometheus.prometheus_job,
            registry=CognitePrometheus.registry,
            handler=auth_handler
        )

    def get_gauge(self, name: str, description: str):
        return Gauge(name, description, registry=CognitePrometheus.registry)
