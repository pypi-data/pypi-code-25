import requests
def  getResponse(method ,url, **kwargs):
    if method == 'GET':
        r = requests.get(url);
    else:
        r = requests.post(url,json=kwargs['jsondata']);
    return  r.json()

def test():
    url = 'https://api.qingcloud.com/iaas/?access_key_id=QYACCESSKEYIDEXAMPLE&action=DescribeInstances&limit=20&signature_method=HmacSHA256&signature_version=1&status.1=running&time_stamp=2013-08-29T06%3A42%3A25Z&version=1&zone=pek3b&signature=ihPnXFgsg5yyqhDN2IejJ2%2Bbo89ABQ1UqFkyOdzRITY%3D'
    result = str(getResponse( method='GET',url=url))
    print(result);