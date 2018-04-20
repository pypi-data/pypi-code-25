from collections import OrderedDict

from django.http.request import HttpRequest
from django.views.generic import TemplateView

from rinzler import Rinzler
from rinzler.core.response import Response
from rinzler.core.route_mapping import RouteMapping


class Exemplo2Controller(TemplateView):
    """
    Controller do namespace de end-points /v1/exemplo desta API
    end-points:
     - GET /
     - GET /{id}/
     - POST /
     - PUT /
     - DELETE /{exemplo_id}/
    """

    api_name = "ExemploAPI"
    service = object()

    def connect(self, app: Rinzler) -> RouteMapping:
        """
        Método responsável pelo acoplamento de um end-point a um callback service.
        :param app: Rinzler' object
        :return: object
        """
        router = app.get_end_point_register()

        router.get("/", self.get_exemplo)
        router.get("/{exemplo_id}/", self.get_exemplo_id)
        router.post("/", self.inserir_exemplo)
        router.put("/", self.atualizar_exemplo)
        router.delete("/{exemplo_id}/", self.deletar_exemplo)

        return router

    def get_exemplo(self, request: HttpRequest, app: Rinzler, **params: dict):
        """
        De acordo com a documentação em
        :param request: HttpRequest
        :param app: Rinzler
        :param params: dict
        :return: Response
        """
        try:
            auth_data = app.auth_data
            resultado = {
                'response': "OK"
            }

            response = OrderedDict()
            response['success'] = True
            response["data"] = {
                self.api_name: resultado
            }

            return Response(response, content_type="application/json")
        except RuntimeError as e:
            app['log'].error("Exception: %s" % str(e), exc_info=True)
            return Response(None, content_type="application/json", status=500)

    def get_exemplo_id(self, request: HttpRequest, app: Rinzler, **params: dict):
        """
        De acordo com a documentação em
        :param request: HttpRequest
        :param app: object
        :param params: dict
        :return: Response
        """
        try:
            exemplo_id = str(params['exemplo_id'])

            resultado = {
                'response': app.auth_data
            }

            response = OrderedDict()
            response['success'] = True
            response["data"] = {
                self.api_name: resultado
            }

            return Response(response, content_type="application/json")
        except RuntimeError as e:
            app['log'].error("Exception: %s" % str(e), exc_info=True)
            return Response(None, content_type="application/json", status=500)

    def inserir_exemplo(self, request: HttpRequest, app: Rinzler, **params: dict):
        """
        De acordo com a documentação em
        :param request: HttpRequest
        :param app: object
        :param params: dict
        :return: Response
        """
        try:

            jwt_token = app.auth_data['token']
            jwt_data = app.auth_data['data']

            payload = request.read()

            return Response(None, content_type="application/json", status=201)
        except RuntimeError as e:
            app['log'].error("Exception: %s" % str(e), exc_info=True)
            return Response(None, content_type="application/json", status=500)

    def atualizar_exemplo(self, request: HttpRequest, app: Rinzler, **params: dict):
        """
        De acordo com a documentação em
        :param request: HttpRequest
        :param app: object
        :param params: dict
        :return: Response
        """
        try:

            jwt_token = app.auth_data['token']
            jwt_data = app.auth_data['data']

            payload = request.read()

            return Response(None, content_type="application/json", status=201)
        except RuntimeError as e:
            app['log'].error("Exception: %s" % str(e), exc_info=True)
            return Response(None, content_type="application/json", status=500)

    def deletar_exemplo(self, request: HttpRequest, app: Rinzler, **params: dict):
        """
        De acordo com a documentação em
        :param request: HttpRequest
        :param app: object
        :param params: dict
        :return: Response
        """
        try:
            jwt_token = app.auth_data['token']
            jwt_data = app.auth_data['data']

            payload = request.read()

            return Response(None, content_type="application/json", status=204)
        except RuntimeError as e:
            app['log'].error("Exception: %s" % str(e), exc_info=True)
            return Response(None, content_type="application/json", status=500)
