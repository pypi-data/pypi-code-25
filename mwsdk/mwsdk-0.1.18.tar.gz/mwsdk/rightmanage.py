import requests
from consul import Consul
from collections import namedtuple

User = namedtuple('User', ['uid', 'username', 'issystemuser','ismanageuser','manageuserid'])

class RightmanageError(Exception):
    pass

service_name = 'rightmanage'

class Rightmanage():
    def __init__(self):
        consul = Consul()
        auth_conf = consul.catalog.service(service_name,tag='kong')[1]
        if not auth_conf:
            raise Exception('The %s service is not exist!'%service_name)
        self.ip = auth_conf[0]['ServiceAddress']
        self.port = auth_conf[0]['ServicePort']

    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/rightmanage/v1.0/cur-permissions?systemname=maxguideweb&jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    def cur_permissions(self,systemname,jwt,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        data = {'systemname':systemname,'jwt':jwt}
        resp = requests.get('http://{ip}:{port}/{service}/{version}/cur-permissions'.format(ip=self.ip,
                            port=self.port,version=version,service=service_name),
                      params=data,headers=headers)
        return resp.status_code,resp.json()

    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/rightmanage/v1.0/cur-user?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    def cur_user(self,jwt,version='v1.0'):
        '''
        返回值是json
        {"uid": self.uid,   #user.id
        "uname": self.uname, # user.name
        "systemuser":self.systemuser, #user.issystemuser
            "manageuser":self.manageuser,
            "manageuserid":self.manageuserid}
        '''
        headers = {'Accept': 'chatset=utf8'}
        data = {'jwt':jwt}
        resp = requests.get('http://{ip}:{port}/{service}/{version}/cur-user'.format(ip=self.ip,
                            port=self.port,version=version,service=service_name),
                      params=data,headers=headers)
        return resp.status_code,resp.json()

    def login_user(self,jwt,version='v1.0'):
        _, user_js = self.cur_user(jwt,version)
        return User(uid=user_js['uid'],
                    username=user_js['uname'],
                    issystemuser=user_js['systemuser'],
                    ismanageuser=user_js['manageuser'],
                    manageuserid=user_js['manageuserid']
                    )

if __name__ == '__main__':
    rm = Rightmanage()
    # print(auth.login_jwt('ksbus','698d51a19d8a121ce581499d7b701668'))
    jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    print(rm.cur_permissions('maxguideweb',jwt))
    print(rm.cur_user(jwt))
