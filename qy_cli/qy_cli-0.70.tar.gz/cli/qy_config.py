import os.path;
filePath = '/.qingcloud/config.yaml'#指定文件所在路径

class qyConfig:

     def __init__(self):
         cf = qyConfig.getConfig();
         if cf:
             self.configmap = cf;
             self.access_key_id  = self.configmap['access_key_id'];
             self.secret_access_key = self.configmap['secret_access_key'];
             self.zone = self.configmap['zone']
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
         result = None
         if not os.path.exists(absoluteFilePath):
             return result
         with open(absoluteFilePath) as f:
             for line in f.readlines():
                 if line == '\n':
                     continue
                 line = line.strip()
                 print(line)
                 str1 = line.split(":")[0]
                 str2 = line.split(":")[-1]
                 str2 = eval(str2)
                 result[str1] = str2;
         return result




