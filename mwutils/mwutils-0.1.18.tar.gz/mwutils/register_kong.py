import requests
import socket

get_host = lambda kong: '{http}{kong}'.format(http='http://' if not kong.startswith('http://') else '',
                                              kong=kong)
replace = lambda service:service.replace('.','_').replace('/','_')
# 补充 /
get_backslash = lambda path:'{bs}{path}'.format(bs='/' if not path.startswith('/') else '',
                                                path=path)

def get_service_host(port):
    return '%s:%s'%( socket.gethostbyname(socket.gethostname()),port)

def reg_swagger_ui(service,service_host,kong_admin='kong_admin'):
    '''
    :param kong_admin: 用于注册服务
    :param service_host: 本地服务的host，用于设定upstream_url
    :param service: 服务api，如：rightmanage/v1.0
    :return: 
    '''
    api_url = '{kong}/apis/'.format(kong=get_host(kong_admin))
    # api_name 前不能有 /
    api_name = '{service}_swagger_ui'.format(service=replace(get_backslash(service)[1:]))
    uris = '{service}/ui'.format(service=get_backslash(service))
    upstream_url = '{service_host}{service}/ui'.format(service_host=get_host(service_host),
                                                      service=get_backslash(service))
    try:
        # 删除旧的api
        requests.delete('{kong}/apis/{api_name}'.format(kong=get_host(kong_admin),
                                                        api_name=api_name))
        # 注册 swagger ui
        resp = requests.post(api_url,
                             json={'name': api_name,
                                   'uris': uris,
                                   'upstream_url': upstream_url})
    except Exception as e:
        print('注册%s的swagger ui 失败,error:%s'%(service,e))
        import sys
        sys.exit(-1)
    print('注册 %s swagger ui 成功'%service, resp.text)

def reg_swagger_json(service,service_host,kong_admin='kong_admin'):
    '''
    :param kong_admin: 用于注册服务
    :param service_host: 本地服务的host，用于设定upstream_url
    :param service: 服务api，如：rightmanage/v1.0
    :return: 
    '''
    ''''
        # 注册 swagger json
    resp = requests.post('http://{kong}/apis/'.format(kong=KONG),
                         json={'name': 'rightmanage_swagger_json',
                               'uris': '/rightmanage/v1.0/swagger.json',
                               'upstream_url': 'http://{server}/rightmanage/v1.0/swagger.json'.format(server=SERVER)})
    print('注册 swagger json', resp.text)

    '''
    api_url = '{kong}/apis/'.format(kong=get_host(kong_admin))
    # api_name 前不能有 /
    api_name = '{service}_swagger_json'.format(service=replace(get_backslash(service)[1:]))
    uris = '{service}/swagger.json'.format(service=get_backslash(service))
    upstream_url = '{service_host}{service}/swagger.json'.format(service_host=get_host(service_host),
                                                      service=get_backslash(service))
    try:
        # 删除旧的api
        requests.delete('{kong}/apis/{api_name}'.format(kong=get_host(kong_admin),
                                                        api_name=api_name))
        # 注册 swagger ui
        resp = requests.post(api_url,
                             json={'name': api_name,
                                   'uris': uris,
                                   'upstream_url': upstream_url})
    except Exception as e:
        print('注册%s的swagger json 失败,error:%s'%(service,e))
        import sys
        sys.exit(-1)
    print('注册 %s swagger json 成功'%service, resp.text)

def reg_service(service,service_host,kong_admin='kong_admin',auth='jwt',kong_uris=''):
    '''
    :param kong_admin: 用于注册服务
    :param service_host: 本地服务的host，用于设定upstream_url
    :param service: 服务api，如：rightmanage/v1.0
    :param kong_uris: 空的host uris，为空时值为service,如：rightmanage/v1.0
    :param auth: 认证类型，可为str或list，如：'jwt'，或：['jwt','key']
    :return: 
    '''
    ''''
    # 注册 服务API
    resp = requests.post('http://{kong}/apis/'.format(kong=KONG),
                         json={'name': 'rightmanage_v1.0',
                               'uris': '/rightmanage/v1.0',
                               'upstream_url': 'http://{server}/rightmanage/v1.0'.format(server=SERVER)})
    print('注册 服务API', resp.text)

    resp = requests.post('http://{kong}/apis/rightmanage_v1.0/plugins'.format(kong=KONG),
                         json={"name": "jwt"})
    print('注册服务API JWT', resp.text)
    '''

    api_url = '{kong}/apis/'.format(kong=get_host(kong_admin))
    api_name = replace(get_backslash(service)[1:])
    if kong_uris:
        uris = '{service}'.format(service=get_backslash(kong_uris))
    else:
        uris = '{service}'.format(service=get_backslash(service))
    upstream_url = '{service_host}{service}'.format(service_host=get_host(service_host),
                                                      service=get_backslash(service))
    try:
        # 删除旧的api
        requests.delete('{kong}/apis/{api_name}'.format(kong=get_host(kong_admin),
                                                        api_name=api_name))
        resp = requests.post(api_url,
                             json={'name': api_name,
                                   'uris': uris,
                                   'upstream_url': upstream_url,
                                   'preserve_host':True})
        print('注册服务成功,',resp.text)
    except Exception as e:
        print('注册 %s服务失败,error:%s'%(service,e))
        import sys
        sys.exit(-1)
    if auth:
        if isinstance(auth, str):
            auth, auth_str = [], auth
            auth.append(auth_str)
        if 'jwt' in auth:
            resp = requests.post('{kong}/apis/{api_name}/plugins'.format(kong=get_host(kong_admin),
                                                                         api_name=api_name),
                                 json={"name": "jwt",
                                       "config.uri_param_names": "jwt",
                                       "config.claims_to_verify": "exp",
                                       "config.key_claim_name": "iss",
                                       "config.secret_is_base64": "false"})
            print('注册服务API JWT 成功', resp.text)
        else:
            raise Exception('不支持的auth(%s)' % auth)




