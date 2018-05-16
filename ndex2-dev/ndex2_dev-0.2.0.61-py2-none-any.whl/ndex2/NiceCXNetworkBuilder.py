from ndex2.niceCXNetwork import NiceCXNetwork


class NiceCXNetworkBuilder(object):
    def __init__(self):
        self.metadata = {}
        self.nice_cx = NiceCXNetwork(user_agent='niceCx Builder')
        self.node_id_lookup = {}




    def set_context(self, context):
        self.nice_cx.set_context(context)


    #def add_node(self, name, represents):