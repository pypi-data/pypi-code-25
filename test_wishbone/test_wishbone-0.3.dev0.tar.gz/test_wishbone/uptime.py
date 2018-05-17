from wishbone.function.template import TemplateFunction
from uptime import uptime


class Uptime(TemplateFunction):

    def get(self):
        return uptime()
