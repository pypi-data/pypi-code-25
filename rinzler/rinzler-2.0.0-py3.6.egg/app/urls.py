"""DriveAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import rinzler
from app.exemplo2_controller import Exemplo2Controller
from app.exemplo_controller import ExemploController
from app.jwt_service import JwtService
from app.settings import CONFIG

from rinzler.core.main_controller import MainController

app = rinzler.boot("ExemploAPI")

app.set_auth_service(JwtService(CONFIG, app))

urlpatterns = [
    app.mount('v1', ExemploController),
    app.mount('v2', Exemplo2Controller),
    app.mount('', MainController)
]
