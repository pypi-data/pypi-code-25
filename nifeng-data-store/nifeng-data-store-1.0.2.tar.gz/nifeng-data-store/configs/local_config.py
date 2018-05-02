from .config import BasicConfig


class LocalConfig(BasicConfig):
    LOG_PATH = 'local_logs'
    MONGO_USER = 'tao'
    MONGO_PASSWORD = '000000'

    JWT_SECRET_KEY = 'super-secret'
    CRYPTO_KEY = 'U70eDgRUKo1D4bCJcsyBkGVDLrBWFrJRsHdqjIs_CiE='
