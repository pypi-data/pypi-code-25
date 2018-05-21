import argparse
from cli.qy_config import qyConfig;
from cli.qy_url import httpUrl;
import requests
import traceback
import json
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
        setOpthonArgsForDescInstance(list_parser1)

        # run-instances
        list_parser2 = subparsers.add_parser('run-instances', help='run-instances');
        setOpthonArgsForRunInstance(list_parser2)


        #terminate-instances
        list_parser3 = subparsers.add_parser('terminate-instances', help='terminate-instances');
        # 设定相应的可选参数
        setOpthonArgsForTurminateInstance(list_parser3)


        self.args = self.parser.parse_args();
        self.argsDict = self.args.__dict__;

        #输入参数字典
        self.argsDict = delDictNone(self.argsDict);
        #移除service
        self.argsDict.pop('service')
        #更改动作参数值
        if self.argsDict['action'] == 'describe-instances':
            self.argsDict['action'] = 'DescribeInstances'
        elif self.argsDict['action'] == 'run-instances':
            self.argsDict['action'] = 'RunInstances'
        elif self.argsDict['action'] == 'terminate-instances':
            self.argsDict['action'] = 'TerminateInstances'

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
    try:
        if method == 'GET':
            r = requests.get(url);
        else:
            r = requests.post(url, json=kwargs['jsondata']);
        return r
    except Exception:
        traceback.print_exc()
        return '!!!'

def setOpthonArgsForDescInstance(list_parser1):
    """
    设置获取主机命令的可选参数
    :param list_parser1:
    :return:
    """
    list_parser1.add_argument("-z", "--ZONE",
                              help="the ID of zone you want to access, this will override");
    list_parser1.add_argument("-f", "--config",
                              help="config file of your access keys");
    list_parser1.add_argument("-O", "--offset", type=int,
                              help="the starting offset of the returning results.");
    list_parser1.add_argument("-l", "--limit", type=int,
                              help="specify the number of the returning results.");
    list_parser1.add_argument("-T", "--tags",
                              help="the comma separated IDs of tags.");
    list_parser1.add_argument("-i", "--instances",
                              help="the comma separated IDs of instances you want to");
    list_parser1.add_argument("-s", "--status",
                              help="instance status: pending, running, stopped,terminated, ceased");
    # list_parser1.add_argument("-m", "--image_id",
    #                           help="the image id of instances");
    list_parser1.add_argument("-t", "--instance_type",
                              help="instance type: small_b, small_c, medium_a, medium_b,medium_c, large_a, large_b, large_c");
    list_parser1.add_argument("-W", "--search_word",
                              help="the combined search column");
    list_parser1.add_argument("-V", "--verbose",
                              help="the number to specify the verbose level, larger thenumber, the more detailed information will bereturned.");


def setOpthonArgsForRunInstance(list_parser2):
    """
    设置创建主机命令的可选参数
    :param list_parser2:
    :return:
    """
    # 设定相应的可选参数


    list_parser2.add_argument("-z", "--ZONE",help="the ID of zone you want to access, this will override");
    list_parser2.add_argument("-m", "--image_id", help="image ID");
    list_parser2.add_argument("-f", "--config",help="config file of your access keys");
    list_parser2.add_argument("-t", "--instance_type",choices = { 'c1m1','c1m2','c1m4','c2m2','c2m4','c2m8','c4m4','c4m8','c4m16'},
                              help="instance type: small_b, small_c, medium_a, medium_b,medium_c, large_a, large_b, large_c");
    list_parser2.add_argument("-i", "--instance_class",help="instance class: 0 is performance; 1 is high performance, default 0.");
    list_parser2.add_argument("-c", "--count",type=int,
                              help="the number of instances to launch, default 1.");
    list_parser2.add_argument("-C", "--cpu",type=int,choices = {1, 2, 4, 8, 16 },
                              help="cpu core: 1, 2, 4, 8, 16");
    list_parser2.add_argument("-m", "--memory", type=int, choices={512, 1024, 2048, 4096, 8192, 16384},
                              help="memory size in MB: 512, 1024, 2048, 4096, 8192, 16384");
    list_parser2.add_argument("-N", "--instance_name",help="instance name");
    list_parser2.add_argument("-n", "--vxnets",help="specifies the IDs of vxnets the instance will join.");
    list_parser2.add_argument("-s", "--security_group",help="the ID of security group that will be applied to instance");
    list_parser2.add_argument("-l", "--login_mode",choices = { 'keypair','passwd'},help="SSH login mode: keypair or passwd");
    list_parser2.add_argument("-p", "--login_passwd",help="login_passwd, should specified when SSH login mode is passwd.");
    list_parser2.add_argument("-k", "--login_passwd",help="login_keypair, should specified when SSH login mode is keypair");
    list_parser2.add_argument("--hostname",help="the hostname you want to specify for the new instance.");
    list_parser2.add_argument("--need_userdata",help="use userdata");
    list_parser2.add_argument("--userdata_type",help="userdata_type: plain, exec, tar");
    list_parser2.add_argument("--userdata_value",help="userdata_value");
    list_parser2.add_argument("--userdata_path",help="userdata_path");
    list_parser2.add_argument("--cpu_max",type = int,choices = {1, 2, 4, 8, 16 },
                              help="The cpu core, e.g. '1, 2, 4, 8, 16''.");


def setOpthonArgsForTurminateInstance(list_parser3):
    list_parser3.add_argument("-z", "--ZONE",
                              help="the ID of zone you want to access, this will override");
    list_parser3.add_argument("-f", "--config", help="config file of your access keys");
    list_parser3.add_argument("-i", "--instances",
                              help="the comma separated IDs of instances you want to");


#命令入口
def test():
    #读取配置
     v_config = qyConfig();
     if not v_config.configDict:
         print('config file [/root/.qingcloud/config.yaml] not exists or error')
     else:
         cli_instance = cli();
         http_url = httpUrl(cli_instance.argsDict, v_config.configDict);
         print(http_url.url)
         result = json.dump(getResponse(method='GET', url=http_url.url), indent=4)
         print(result);






















