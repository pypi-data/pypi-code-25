

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def create_option_leg_with_option_contract(option_contract,
                                               direction,
                                               quantity):
        from swagger_client.mercury.client.model import OptionLeg

        return OptionLeg(expiration_date=option_contract.expiration_date,
                         direction=direction,
                         type='CALL' if option_contract.call else 'PUT',
                         quantity=quantity,
                         strike=option_contract.strike)
