

#from views.auth import ppssauthpolicy,ACLRoot,getPrincipals
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import transaction
import zope.sqlalchemy

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


def initAuthDb(settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    factory = sessionmaker()
    factory.configure(bind=engine)
    #dbsession = get_tm_session(session_factory, transaction.manager)
    dbsession = factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction.manager)
    with transaction.manager:
        initdb(dbsession,Conf.initdb)
    

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

    config.add_route('ppsschangepassword', '/password/change')
    config.add_route('ppssaddcreateuser', '/user/modify/{userid}')
    config.add_route('ppsslistuser', '/user/list')


    initAuthDb(settings)

    from views.auth import AuthController

    config.add_view(AuthController,attr='login',route_name="ppsslogin", renderer=Conf.logintemplate)
    config.add_view(AuthController,attr='logout',route_name="ppsslogout")
    config.add_view(AuthController,attr='ppsschangepassword',route_name="ppsschangepassword", 
        permission="login", renderer=Conf.changepasswordtemplate)
    config.add_view(AuthController,attr='addUser',route_name="ppssaddcreateuser",
        permission="modifyuser", renderer=Conf.modifyusertemplate)
    config.add_view(AuthController,attr='listuser',route_name="ppsslistuser",
        permission="listuser", renderer=Conf.listusertemplate)

    from views.auth import getPrincipals,ACLRoot
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=getPrincipals) )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(ACLRoot)
    pass
