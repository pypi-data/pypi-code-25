from request import Request
from config import Config
from libs.instance import start_on_demand_instances
from libs.instance import cancel_on_demand_instances
import libs.logger as logger

class test:
    test = None

request = Request(test())
request.aws_profile = 'bjs'
request.aws_region = 'cn-northwest-1'

config = Config(request)
# start_on_demand_instances(config, 1)
cancel_on_demand_instances(config, 1)
