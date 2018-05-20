import datetime
from cli.qy_signature import getSignature
method = 'GET';
uri = 'https://api.qingcloud.com/iaas/';
uri_jm = '/iaas/';
"""
构建请求的url
"""
class httpUrl:
     def __init__(self,url_map,config_dict):
         """

         :param url_map: 可选参数字典
         :param kwargs: 配置参数字典
         """
         self.urldict = url_map;
         self.zone = config_dict['zone'];
         self.access_key_id = config_dict['access_key_id'];
         self.secret_access_key = config_dict['secret_access_key']
         self.getRequestArgs();

         #获取请求url
         self.url = uri + httpUrl.parse_url(self.urldict)


     def getRequestArgs(self):
         """
         公共参数处理
         :return:
         """

         #如何没有指定zone，那么取配置文件的zone
         if not 'zone' in self.urldict:
             self.urldict['zone'] = self.zone;

         time_stamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ");
         self.urldict['time_stamp'] = time_stamp

         access_key_id = self.access_key_id;
         self.urldict['access_key_id'] = access_key_id

         version = 1;
         self.urldict['version'] = version

         signature_method = 'HmacSHA256';
         self.urldict['signature_method'] = signature_method;

         signature_version = 1;
         self.urldict['signature_version'] = signature_version
         signature = getSignature(method,uri_jm,self.urldict,self.secret_access_key);
         self.urldict['signature'] = signature



     @staticmethod
     def parse_url(data={}):
         """
         构造URL 中参数部分
         :param data: 请求参数字典
         :return:url中参数部分
         """
         item = data.items()
         urls = "?"
         for i in item:
             (key, value) = i
             temp_str = key + "=" + str(value)
             urls = urls + temp_str + "&"
         urls = urls[:len(urls) - 1]
         return urls


