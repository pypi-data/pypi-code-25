class RepoException(Exception):
    def __init__(self, err='数据库配置错误！'):
        Exception.__init__(self, err)
