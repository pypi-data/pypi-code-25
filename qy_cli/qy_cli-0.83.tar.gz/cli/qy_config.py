import os.path;
filePath = '/.qingcloud/config.yaml'#指定文件所在路径
import traceback
class qyConfig:

     def __init__(self):
         cf = qyConfig.getConfig();
         if cf:
             self.access_key_id  = self.configmap['qy_access_key_id'];
             self.secret_access_key = self.configmap['qy_secret_access_key'];
             self.zone = self.configmap['zone']

             #配置文件中字段和报文中字段不一致
             self.configmap['access_key_id'] = self.access_key_id
             self.configmap['secret_access_key'] = self.secret_access_key
             self.configmap['zone'] = self.zone
         else:
            self.configmap = None

     @staticmethod
     def getConfig():
         """
         获取配置文件参数access_key_id 、secret_access_key 、zone
         :return:
         """
         # 指定文件所在绝对路径
         absoluteFilePath = os.path.expanduser('~') + filePath
         result = { }
         if not os.path.exists(absoluteFilePath):
             return None

         try:
             with open(absoluteFilePath) as f:
                 for line in f.readlines():
                     if line == '\n':
                         continue
                     line = line.strip()
                     str1 = line.split(":")[0]
                     str2 = line.split(":")[-1]
                     str2 = eval(str2)
                     result[str1] = str2;
         except Exception :
             result = None
         finally:
             return result



