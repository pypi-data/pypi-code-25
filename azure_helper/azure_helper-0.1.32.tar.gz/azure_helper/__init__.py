#! python3

from .apim import *
from .environments import *
from .azure_token import *
from .users import *
from .products import *
from .subscriptions import *
from .web_api import *
from .helpers import *
from .constants import *
from .groups import *


__all__ = [
    "apim",
    "environments",
    "azure_token",
    "users",
    "products",
    "subscriptions",
    "web_api",
    "helpers",
    "constants",
    "groups"
]

apiVersion= "api-version=2016-07-07"