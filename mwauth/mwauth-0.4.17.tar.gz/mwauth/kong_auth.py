from mwauth.base_auth import BaseAuth,User
from flask import request,make_response,g,current_app,session
from functools import wraps
from .redis_session import RedisSessionInterface
class KongAuth(BaseAuth):
    # '''
    # 1，在request前提取 user info
    # '''
    def __set_auth(self):
        '''
        保存用户，jwt等auth info
        :return:
        '''
        if not isinstance(current_app.session_interface,RedisSessionInterface):
            raise Exception('请在app/__init__.py的create_app_swagger方法中增加下列代码：\n app.session_interface = RedisSessionInterface(app, rds)')
        if current_app.config.get('DEVELOPMENT', False):
            g.user_name = current_app.config.get('LOGIN_USER_NAME')  # 'user_dev'
            g.user_id = current_app.config.get('LOGIN_USER_ID')
            g.current_user = User(uid=current_app.config.get('LOGIN_USER_ID'),
                                  uname=current_app.config.get('LOGIN_USER_NAME'),
                                  systemuser=current_app.config.get('LOGIN_USER_SYSTEMUSER', False),
                                  manageuser=current_app.config.get('LOGIN_USER_MANAGEUSER', False),
                                  manageuserid=current_app.config.get('LOGIN_USER_MANAGEUSER_ID'))
            g.jwt = session.sid
            session.update({'uid':g.current_user.uid,'uname':g.current_user.uname,
                            'systemuser':g.current_user.systemuser,
                            'manageuser':g.current_user.manageuser,
                            'manageuserid':g.current_user.manageuserid})
            return
        # 通过了jwt 认证的 api 一定会回传username和userid，否则视为kong的认证不成功
        g.user_name = request.headers.get('X-Consumer-Username')
        g.user_id = request.headers.get('X-Consumer-Custom-Id')
        g.jwt = request.args.get('jwt')
        if g.jwt is None:
            # jwt header authorization: bearer jwt...
            jwt = request.headers.get('authorization', None)
            if jwt:
                # 去掉前面的bearer
                g.jwt = jwt[7:]
            elif session:
                g.jwt = session.sid
                # session 认证可能不经过kong，但也需保证auth 成功，确保代码兼容
                g.user_name = session.get('uname')
                g.user_id = session.get('uid')
            else:
                assert False,'header，query，和cookie中都没有 jwt？'
        if not session:
            # 当非session认证时，还需保存session，保证app中的代码的兼容性
            session.sid = g.jwt
            # 临时session 不需要送cookie，避免浪费流量
            session.seend_cookie = False
            mysession = current_app.session_interface.get_session(g.jwt)
            session.update(dict(mysession))
        g.current_user = User(uid=session.get('uid'), uname=session.get('uname'),
                              systemuser=session.get('systemuser', False),
                              manageuser=session.get('manageuser', False),
                              manageuserid=session.get('manageuserid'))


    def __init__(self, app=None):
        super(KongAuth, self).__init__()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.auth = self
        # self.app.register_blueprint(auth)

    def valid_login(self, func):
        @wraps(func)
        def _request_login(*args, **kw):
            # 给g 赋 用户等信息
            self.__set_auth()
            if g.user_name or g.user_id :
                return func(*args, **kw)
            # 没有认证则返回401
            response = make_response()
            response.status_code = 401
            return response
        return _request_login

# @auth.before_app_request
# def before_app_request():
#     if current_app.config.get('DEVELOPMENT',False):
#         g.user_name = current_app.config.get('LOGIN_USER_NAME')#'user_dev'
#         g.user_id = current_app.config.get('LOGIN_USER_ID')
#         g.jwt = ''
#         return
#     else:
#         g.user_name = request.headers.get('X-Consumer-Username')
#         g.user_id = request.headers.get('X-Consumer-Custom-Id')
#     g.jwt = request.args.get('jwt')
#     if g.jwt is None:
#         # jwt header authorization: bearer jwt...
#         jwt = request.headers.get('authorization', None)
#         if jwt:
#             # 去掉前面的bearer
#             g.jwt = jwt[7:]



