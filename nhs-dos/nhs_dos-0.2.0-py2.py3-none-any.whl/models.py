from nhs_dos.endpoints import Endpoint


class Service:
    def __init__(self, service_json):
        self.json = service_json
        self.id = service_json['id']
        self.name = service_json['name']
        self.endpoints = []
        for ep in service_json['endpoints']:
            self.endpoints.append(Endpoint(ep))


class ServiceList:
    def __init__(self, service_list=None):

        self._service_list = []

        for service in service_list:
            self._service_list.append(service)
