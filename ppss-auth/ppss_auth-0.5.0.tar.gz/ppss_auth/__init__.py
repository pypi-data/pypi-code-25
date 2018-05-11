

#from views.auth import ppssauthpolicy,ACLRoot,getPrincipals
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import SessionAuthenticationPolicy
from constants import Conf
from models import initdb


from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,
    Everyone,ALL_PERMISSIONS
    )


configured = False
def includeme(config):
    global configured
    if configured:
        return
    configured = True
    #ppssauthpolicy = PPSSAuthenticationPolicy(config.get_settings())
    settings = config.get_settings()
    Conf.setup(settings)
    config.include("pyramid_beaker")
    config.add_route('ppsslogin', '/login')
    config.add_route('ppsslogout', '/logout')
    from views.auth import AuthController


    config.add_view(AuthController,attr='login',route_name="ppsslogin", renderer=Conf.logintemplate)
    config.add_view(AuthController,attr='logout',route_name="ppsslogout")


    from views.auth import getPrincipals,ACLRoot
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=getPrincipals) )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(ACLRoot)
    pass
