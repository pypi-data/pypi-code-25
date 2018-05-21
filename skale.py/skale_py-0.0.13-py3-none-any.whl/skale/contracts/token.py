from skale.contracts import BaseContract
import skale.utils.helper as Helper

class Token(BaseContract):
  def __init__(self, skale):
    data = Helper.get_abi()
    name = 'token'
    super().__init__(skale, name, data[f'{name}_address'], data[f'{name}_abi'] )
