import argparse
from cli.qy_config import qyConfig;
from cli.qy_url import httpUrl;
import requests

"""
命令行类
"""
class cli:
    def __init__(self):
        self.parser = argparse.ArgumentParser();

        # 位置参数service ，此处固定为iaas，默认参数类型是string ,可以使用type = int 设置整形
        self.parser.add_argument("service", choices=['iaas'], help="choose service ")


        #为动作嵌套解析器，不同动作绑定不同可选参数
        subparsers = self.parser.add_subparsers(dest='action',help='action');

        #describe-instances
        list_parser1 = subparsers.add_parser('describe-instances', help='describe-instances');
        # 设定相应的可选参数
        list_parser1.add_argument("-z", "--ZONE",
                                 help="the ID of zone you want to access, this will override");
        list_parser1.add_argument("-f", "--config",
                                 help="config file of your access keys");
        list_parser1.add_argument("-O", "--offset",type=int,
                                 help="the starting offset of the returning results.");
        list_parser1.add_argument("-l", "--limit",type=int,
                                 help="specify the number of the returning results.");
        list_parser1.add_argument("-T", "--tags",
                                 help="the comma separated IDs of tags.");
        list_parser1.add_argument("-i", "--instances",
                                 help="the comma separated IDs of instances you want to");
        list_parser1.add_argument("-s", "--status",
                                 help="instance status: pending, running, stopped,terminated, ceased");
        list_parser1.add_argument("-m", "--image_id",
                                 help="the image id of instances.");
        list_parser1.add_argument("-t", "--instance_type",
                                 help="instance type: small_b, small_c, medium_a, medium_b,medium_c, large_a, large_b, large_c");
        list_parser1.add_argument("-W", "--search_word",
                                 help="the combined search column");
        list_parser1.add_argument("-V", "--verbose",
                                 help="the number to specify the verbose level, larger thenumber, the more detailed information will bereturned.");

        # run-instances
        list_parser2 = subparsers.add_parser('run-instances', help='run-instances');
        # 设定相应的可选参数
        list_parser2.add_argument("-z", "--ZONE",
                                 help="the ID of zone you want to access, this will override");
        list_parser2.add_argument("-m", "--image_id", help="image ID");

        #terminate-instances
        list_parser3 = subparsers.add_parser('terminate-instances', help='terminate-instances');
        # 设定相应的可选参数
        list_parser3.add_argument("-z", "--ZONE",
                                 help="the ID of zone you want to access, this will override");
        list_parser3.add_argument("-O", "--offset", type=int, help="the starting offset of the returning results.");


        self.args = self.parser.parse_args();
        self.argsDict = self.args.__dict__;

        #输入参数字典
        self.argsDict = delDictNone(self.argsDict);

def delDictNone(odict):
    """
    去掉字典中值为none的item
    :param odict:
    :return:
    """
    ndict = {};
    for key,value in odict.items():
        if  value != None:
            ndict[key] = value
    return ndict;

def  getResponse(method ,url, **kwargs):
    if method == 'GET':
        r = requests.get(url);
    else:
        r = requests.post(url,json=kwargs['jsondata']);
    return  r.json()

#命令入口
def test():
    #读取配置
     v_config = qyConfig();
     if not v_config.configDict:
         print('config file [/root/.qingcloud/config.yaml] not exists or error')
     else:
         cli_instance = cli();
         http_url = httpUrl(cli_instance.argsDict, v_config.configDict);
         print(http_url)
         result = str(getResponse(method='GET', url=http_url))
         print(result);






















