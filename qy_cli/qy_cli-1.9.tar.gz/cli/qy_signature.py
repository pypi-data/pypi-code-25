
from urllib.parse import quote
import urllib;
import base64
import hmac
from hashlib import sha256

"""
使用getSignature 获取签名
"""


#构造URL请求参数部分
def getSignatureArgs(str_map):
    # 字典排序
    # str_url = sort_dict(str_map);

    #构造url
    str_url = sortDict(str_map);
    print(str_url)

    #对参数名称和参数值进行URL编码
    str_url = percentEncode(str_url)
    return  str_url;


def getSignatureStr(method,uri,url):
    """
    #构造被签名的串，被签名串 = HTTP请求方式 + “\n” + uri + “\n” + url 请求串
    :param method:
    :param uri:
    :param url:
    :return:
    """
    str = method + "\n" + uri + "\n"+ url;
    return  str;

def percentEncode(str):
    res = str.replace(' ', '%20')
    res = str.replace(':', '%3A')
    return res


def sort_dict(dict_words):
    """
    字典排序
    :param dict_words:
    :return:
    """
    keys = sorted(dict_words)
    result = { };
    keys = list(keys)
    for key in keys:
        result[key] = dict_words[key];
    return result

def getSignature(method,uri,url_map,secret_access_key):
    """
    获取签名
    :param method:请求方法
    :param uri:请求的uri路径
    :param url_map:请求参数字典
    :param secret_access_key:私钥
    :return:签名
    """

    url =  getSignatureArgs(url_map);
    string_to_sign = getSignatureStr(method,uri,url);
    sb = bytes(secret_access_key, encoding="utf8")

    h = hmac.new(sb, digestmod=sha256)
    h.update(string_to_sign.encode("utf8"))
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.parse.quote_plus(sign)
    return  signature;


def sortDict(odict):
    url = "";
    keys = sorted(odict)
    keys = list(keys)
    for key in keys:
        url = url+ str(key) + '='+ str(odict[key]) + '&'
    url = url[:-1]
    return url



def test():
    """
    测试的
    :return:
    """
    url_map = {
      "count":1,
      "vxnets.1":"vxnet-0",
      "zone":"pek1",
      "instance_type":"small_b",
      "signature_version":1,
      "signature_method":"HmacSHA256",
      "instance_name":"demo",
      "image_id":"centos64x86a",
      "login_mode":"passwd",
      "login_passwd":"QingCloud20130712",
      "version":1,
      "access_key_id":"QYACCESSKEYIDEXAMPLE",
      "action":"RunInstances",
      "time_stamp":"2013-08-27T14:30:10Z"
    };
    s_url = 'GET\n/iaas/\naccess_key_id=QYACCESSKEYIDEXAMPLE&action=RunInstances&count=1&image_id=centos64x86a&instance_name=demo&instance_type=small_b&login_mode=passwd&login_passwd=QingCloud20130712&signature_method=HmacSHA256&signature_version=1&time_stamp=2013-08-27T14%3A30%3A10Z&version=1&vxnets.1=vxnet-0&zone=pek1'

    url_dict = {
        "count": 1,
        "vxnets.1": "vxnet-0",
        "zone": "pek1",
        "instance_type": "small_b",
        "instance_name": "demo",
        "image_id": "centos64x86a",
        "login_mode": "passwd",
        "login_passwd": "QingCloud20130712",
        "action": "RunInstances",
        "time_stamp": "2013-08-27T14:30:10Z"
    };
    s_s = '32bseYy39DOlatuewpeuW5vpmW51sD1A%2FJdGynqSpP8%3D';
    method = 'GET';
    uri = "/iaas/";
    secret_access_key = 'SECRETACCESSKEY'
    cf = { };
    cf['zone'] = "pek1";
    cf['access_key_id'] = "QYACCESSKEYIDEXAMPLE"
    cf['secret_access_key'] = 'SECRETACCESSKEY'
    uuu = 'https://api.qingcloud.com/iaas/?access_key_id=QYACCESSKEYIDEXAMPLE&action=RunInstances&count=1&image_id=centos64x86a&instance_name=demo&instance_type=small_b&login_mode=passwd&login_passwd=QingCloud20130712&signature_method=HmacSHA256&signature_version=1&time_stamp=2013-08-27T14%3A30%3A10Z&version=1&vxnets.1=vxnet-0&zone=pek1&signature=32bseYy39DOlatuewpeuW5vpmW51sD1A%2FJdGynqSpP8%3D'
    uul = 'https://api.qingcloud.com/iaas/?access_key_id=WYLVVPSXZQQHPHAQTWEQ&action=DescribeInstances&signature_method=HmacSHA256&signature_version=1&time_stamp=2018-05-20T14%3A19%3A26Z&version=1&zone=pek3b&signature=7oCdxDw3z7%2BrcY4p3qRuluXDR%2Fq3plAOfxCfOtgfDwU%3D'
    from cli.qy_url import httpUrl;
    hu = httpUrl(url_dict,cf)
    print(hu.url)
    print(uuu)
    print(uuu == hu.url)
    result = getResponse(method='GET', url=uuu)
    print(result);

def  getResponse(method ,url, **kwargs):
    import traceback
    import requests
    try:
        if method == 'GET':
            r = requests.get(url);
        else:
            r = requests.post(url, json=kwargs['jsondata']);
        print(r)
        return r.json()
    except Exception:
        traceback.print_exc()
        return '!!!'