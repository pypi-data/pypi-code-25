from .config import BasicConfig


class ProductionConfig(BasicConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:000000@localhost/assets_center'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'super-secret'
    CRYPTO_KEY = 'U70eDgRUKo1D4bCJcsyBkGVDLrBWFrJRsHdqjIs_CiE='
