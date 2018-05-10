'''
window下的測試
consul agent -server -bootstrap-expect 1 -data-dir data-dir -bind=127.0.0.1 -ui-dir ./consul_ui/ -rejoin -config-dir=consul.d -client 0.0.0.0
curl http://127.0.0.1:8500/v1/catalog/services
'''
from consul import Consul

def reg_service(name,address =None,port=None,tags=None,check=None,token=None):
    '''
    :param name:服務名稱
    :param address: 服務ip
    :param port: 服務 port
    :param tags:
    :param check:
    :param token:
    :return:
    '''
    cons = Consul()
    try:
        agent_self = cons.agent.self()
    except Exception as e:
        print('访问consul失败,error:%s' % ( e))
        import sys
        sys.exit(-1)
    member = agent_self['Member']
    node_name = member.get('Name')
    if not address:
        address = member.get('Addr')
    try:
        cons.agent.service.register(name,service_id='%s:%s:%s'%(node_name,name,port or ''),address=address,port=port,tags=tags,check=check,token=token)
        print('註冊%s到consul成功！'%name)
    except Exception as e:
        print('注册 %s服务失败,error:%s' % (name, e))
        import sys
        sys.exit(-1)

def dereg_service(name,web_port):
    cons = Consul()
    try:
        agent_self = cons.agent.self()
        member = agent_self['Member']
        node_name = member.get('Name')
        service_id='%s:%s:%s'%(node_name,name,web_port or '')
        cons.agent.service.deregister(service_id)
        print('删除(%s)成功！'%name)
    except Exception as e:
        print('删除 %s服务失败,error:%s' % (name, e))
        import sys
        sys.exit(-1)

class AgentConf():
    '''
    獲取本機agent 的nodename，ip和consul 集群內的service
    '''
    def __init__(self):
        consul = Consul()
        try:
            agent_self = consul.agent.self()
            member = agent_self['Member']
            self._node_name = member.get('Name')
            self._bind_ip = member.get('Addr',)
            self._services = consul.catalog.services()[1]
        except Exception as e:
            print('读取consul 服务失败,error:%s' % (e))
            import sys
            sys.exit(-1)

    @property
    def node_name(self):
        return self._node_name

    @property
    def bind_ip(self):
        '''
        agent 綁定的IP
        :return:
        '''
        return self._bind_ip

    @property
    def services(self):
        return self._services

class RedisConf():
    '''
    取master 模式的redis的配置，用於寫
    '''
    def __init__(self,tag,db=0,near=False):
        '''
        获取redis的配置
        :param tag:
        :param db: redis的db
        :param near: 取離該節點最近的redis，通常可在本機會部署一個redis
        '''
        consul = Consul()
        if near:
            agent_self = consul.agent.self()
            member = agent_self['Member']
            node_name = member.get('NodeName')
            redis =consul.catalog.service('redis', tag=tag,near=node_name)[1]
        else:
            redis =consul.catalog.service('redis', tag=tag)[1]
        if not redis:
            print('The %s redis config is not exist!'%tag)
            import sys
            sys.exit(-1)
        self._ip =redis[0]['ServiceAddress']
        self._port = redis[0]['ServicePort']
        self._db = db

    @property
    def ip(self):
        return self._ip
    @property
    def port(self):
        return self._port
    @property
    def db(self):
        return self._db
    def redis_url(self):
        return 'redis://%s:%d/%d' % (self.ip,self.port,self.db)


class RedisConfMaster(RedisConf):
    '''
    取master 模式的redis的配置，用於寫
    '''
    def __init__(self):
        super(RedisConfMaster,self).__init__(tag='master')

class RedisConfSlave():
    '''
    離本節點最近的slave redis 的配置，用於讀,沒有讀到slave時，通過設定可使用master配置
    '''
    def __init__(self,onlySlave=True):
        '''
        :param onlySlave: True只使用slave，False slave不存在時取master
        '''
        consul = Consul()
        agent_self = consul.agent.self()
        member = agent_self['Member']
        node_name = member.get('NodeName')
        # 取離該節點最近的redis，通常可在本機會部署一個redis
        redis =consul.catalog.service('redis', tag='slave',near=node_name)[1]
        # 如果沒有取到slave 就取master
        if not redis and not onlySlave:
            redis = consul.catalog.service('redis', tag='master')[1]
            if not redis:
                print('The master redis config is not exist!')
                import sys
                sys.exit(-1)
        if not redis:
            print('The slave redis config is not exist!')
            import sys
            sys.exit(-1)
        self._ip =redis[0]['ServiceAddress']
        self._port = redis[0]['ServicePort']
        self._db = 0

    # @property
    # def ip(self):
    #     return self._ip
    # @property
    # def port(self):
    #     return self._port
    # @property
    # def db(self):
    #     return self._db
    # def redis_url(self):
    #     return 'redis://%s:%d/%d' % (self.ip,self.port,self.db)

class DatabaseConf():
    def __init__(self,dbname='maxbus'):
        '''
        如果dbname 和dbdriver 取不到配置，就直接選擇 database中的第一筆做為配置
        :param dbname:
        :param dbdriver:
        '''
        cons = Consul()
        try:
            db =cons.catalog.service('database', tag=dbname)[1]
            if not db:
                db = cons.catalog.service('database')[1]
            if not db:
                raise Exception('The database config is not exist!')
        except Exception as e:
            print('资料库服务读取失败,%s'%e)
            import sys
            sys.exit(-1)

        self._host =db[0]['ServiceAddress']
        self._port = db[0]['ServicePort']
        def get_value(key):
            kv = cons.kv.get(key)[1]
            if not kv:
                raise Exception('The consul.kv(%s) is not exist!' % key)
            return kv['Value'].decode()
        self._dbdriver = 'mssql+pymssql' if get_value('%s_dbdriver' % dbname) == 'mssql' else 'mysql+mysqldb'
        self._name = get_value('%s_db_name'%dbname)
        self._user = get_value('%s_login_user'%dbname)
        self._password = get_value('%s_login_pw'%dbname)

    @property
    def name(self):
        return self._name
    @property
    def host(self):
        return self._host
    @property
    def port(self):
        return self._port
    @property
    def user(self):
        return self._user
    @property
    def password(self):
        return self._password
    def sqlalchemy_database_uri(self):
        return "{dbdriver}://{us}:{pw}@{host}:{port}/{name}".format(
                 dbdriver =self._dbdriver,us=self._user,pw=self._password,
                 host=self._host,port=self._port,name=self._name)

    def is_null(self):
        '''
        如果是mysql则返回 ifnull，否则返回isnull
        :return: 如果是mysql则返回 ifnull，否则返回isnull
        '''
        return 'ifnull' if self.sqlalchemy_database_uri().startswith('mysql+mysqldb') else 'isnull'

class KongConf():
    '''
    取kong的配置
    '''
    def __init__(self):
        cons = Consul()
        try:
            kong = cons.catalog.service('kong', tag='kong')[1]
            if not kong:
                raise Exception('The kong config is not exist!')
        except Exception as e:
            print('读取kong失败，error:%s'%e)
            import sys
            sys.exit(-1)
        self._ip = kong[0]['ServiceAddress']
        self._port = kong[0]['ServicePort']
        self._agent_ip = kong[0]['Address']

    @property
    def ip(self):
        # kong的ip
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def agent_ip(self):
        # 本機的ip地址
        return self._agent_ip

    def host_url(self):
        return 'http://%s:%d' % (self.ip, self.port)

class KongAdminConf():
    '''
    取kong Admin的配置
    '''
    def __init__(self):
        cons = Consul()
        try:
            kong = cons.catalog.service('kong', tag='admin')[1]
            if not kong:
                raise Exception('The kong admin config is not exist!')
        except Exception as e:
            print('读取kongadmin 失败，%s' % e)
            import sys
            sys.exit(-1)
        self._ip = kong[0]['ServiceAddress']
        self._port = kong[0]['ServicePort']
        self._agent_ip = kong[0]['Address']

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def agent_ip(self):
        # 取得本機IP
        return self._agent_ip

    def host_url(self):
        return 'http://%s:%d' % (self.ip, self.port)

class KafkaConf():
    '''
    取kong Admin的配置
    '''
    def __init__(self):
        cons = Consul()
        try:
            kafkas = cons.catalog.service('kafka',)[1]
            if not kafkas:
                raise Exception('The zookeeper config is not exist!')
        except Exception as e:
            print('读取 kafka 配置失败,%s'%e)
            import sys
            sys.exit(-1)
        self._bootstrap_servers = []
        for kfk in kafkas:
            self._bootstrap_servers.append('%s:%s'%(kfk['ServiceAddress'],
                                                   kfk['ServicePort']))
    @property
    def bootstrap_servers(self):
        return ','.join(self._bootstrap_servers)

class Cassandra():
    '''
    取Cassandra的配置
    '''
    def __init__(self):
        cons = Consul()
        try:
            cassandras = cons.catalog.service('cassandra',)[1]
            if not cassandras:
                raise Exception('The cassandra config is not exist!')
        except Exception as e:
            print('读取 cassandra 配置失败,%s'%e)
            import sys
            sys.exit(-1)
        self._cluster = []
        for cassd in cassandras:
            self._cluster.append(cassd['ServiceAddress'])
    @property
    def cluster(self):
        return self._cluster

if __name__ == '__main__':
    rcw = RedisConfMaster()
    print('rcw',rcw.redis_url())
    rcr = RedisConfSlave(True)
    print('rcr',rcr.redis_url())
    db = DatabaseConf()
    print(db.sqlalchemy_database_uri())
    k = KongConf()
    print(k.host_url())
    kadm = KongAdminConf()
    print(kadm.host_url())
    kfk = KafkaConf()
    print(kfk.bootstrap_servers)
    ag = AgentConf()
    print(ag.bind_addr,ag.node_name,ag.services)