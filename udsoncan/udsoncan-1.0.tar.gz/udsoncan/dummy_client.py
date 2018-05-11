import udsoncan
from udsoncan.Connection import IsoTPConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
from udsoncan.services import *
import udsoncan.configs

def algo(seed, param):
	return  b"\xed\xcb\xa9\x87"

class my_codec(udsoncan.DidCodec):
	def encode(self, s):
		return bytes(s.encode('ascii'))


config = dict(udsoncan.configs.default_client_config)
config['data_identifiers'] = {0xF190 : my_codec}
config['security_algo'] = algo


conn = IsoTPConnection('vcan0', rxid=0x123, txid=0x456)
with Client(conn,  request_timeout=2, config=config) as client:
  try:
     client.change_session(DiagnosticSessionControl.Session.extendedDiagnosticSession)  # integer with value of 3
     client.unlock_security_access(3)   # Fictive security level. Integer coming from fictive lib, let's say its value is 5
     vin = client.write_data_by_identifier(udsoncan.DataIdentifier.VIN, 'ABC123456789')       # Standard ID for VIN is 0xF190. Codec is set in the client configuration
     print('Vehicle Identification Number successfully changed.')
     client.ecu_reset(ECUReset.ResetType.hardReset)  # HardReset = 0x01
  except NegativeResponseException as e:
     print('Server refused our request for service %s with code "%s" (0x%02x)' % (e.response.service.get_name(), e.response.code_name, e.response.code))
  except InvalidResponseException as e:
     print('Server sent an invalid payload : %s' % e.response.original_payload)