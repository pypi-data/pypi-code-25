from pyramid.response import Response
from pyramid.authentication import AuthTktCookieHelper
from pyramid.settings import asbool

from ..constants import Conf
from ..models import PPSsuser,PPSsgroup

from pyramid.view import view_config,forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import os,datetime,logging
l = logging.getLogger('ppssauth')


from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,Deny,
    Everyone,ALL_PERMISSIONS
    )


def getPrincipals(uid,request):
    groups = request.session.get('principals',[])
    l.info("####  usergroups:{g}".format(g=groups))
    return groups

class ACLRoot(object):
    baseACL=[(Allow, Authenticated, 'view'),
        (Allow, 'g:superadmin', ALL_PERMISSIONS),
        (Deny,  'g:admin', 'deleteadmin'),
        (Allow, 'g:admin', ALL_PERMISSIONS)
        ]

    lastupdateACL = datetime.datetime.now()
    __acl__ = [
        (Allow, 'g:superadmin', ALL_PERMISSIONS),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, request):
        self.request = request
        l.info("*************ACLRoot*************")
        groups = self.request.dbsession.query(PPSsgroup).filter(PPSsgroup.enabled==1).all()
        acl = [] 
        for group in groups:
            acl.append( (Allow,
                    str("g:"+group.name),
                    tuple([str(p.name) for p in group.permissions])  
            ) )

        ACLRoot.__acl__ = ACLRoot.baseACL + acl
        l.info("built ACL:{acl}".format(acl=repr(ACLRoot.__acl__)) )



class AuthController():

    def __init__(self,request):
        self.request = request
        self.user = None

    def login(self):
        l.info("trying login")
        r = self.request
        postloginpage = self.request.referer if self.request.referer!=self.request.route_url("ppsslogin") else Conf.postloginroute
        postloginpage = Conf.postloginroute
        if r.POST:
            username = r.params.get("username",u"")
            password = r.params.get("password",u"")
            #l.info("u={username},p={password} ".format(username=username,password=password))
            if username == Conf.adminname and password == Conf.adminpass:
                l.info("{username} logged in as superuser".format(username=username) )
                r.session['admin'] = True
                r.session['principals'] = ["g:admin","g:superadmin"]
                headers = remember(r, u"1")
                r.userid=u"1"
                return HTTPFound(r.route_url(postloginpage),headers=headers)
            res = PPSsuser.checkLogin(username,password,r.dbsession)
            if res:
                l.info("{username} logged in as normal user".format(username=username) )
                r.userid=res.id
                headers = remember(r, res.id)
                r.session['principals'] = [str("g:"+group.name ) for group in res.groups  ]  #["g:user"]
                return HTTPFound(r.route_url(postloginpage),headers=headers)
            self.request.dbsession.query(PPSsuser).filter()    
            return {'logintpl': Conf.logintemplateinherit ,'msg':'something went wrong with your login. Please check your informations'}
        #return Response("ok")
        #return{'logintpl': "arvalpromotool:/templates/layout/bolayout.mako" , 'msg':''}
        return{'logintpl': Conf.logintemplateinherit , 'msg':''}

    def logout(self):
        l.info("logout")
        l.info("principals = {pr}".format(pr=self.request.session.get('principals',[])  ))
        headers = forget(self.request)
        return HTTPFound(self.request.route_url(Conf.logoutroute),headers=headers)