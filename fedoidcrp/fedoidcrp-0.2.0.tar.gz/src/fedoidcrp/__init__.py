# from oidcrp import RPHandler

__version__ = '0.2.0'

#
# class FedRPHandler(RPHandler):
#     def __init__(self, base_url='', hash_seed="", keyjar=None, verify_ssl=True,
#                  services=None, service_factory=None, client_configs=None,
#                  client_authn_factory=None, client_cls=None,
#                  state_db=None, federation_entity=None, **kwargs):
#
#         RPHandler.__init__(self, base_url, hash_seed, keyjar, verify_ssl,
#              services, service_factory, client_configs,
#              client_authn_factory, client_cls, state_db, **kwargs)
#
#         self.federation_entity = federation_entity
#
#     def init_client(self, issuer):
#         client = RPHandler.init_client(self, issuer)
#         client.service_context.federation_entity = self.federation_entity
#         return client
