# -*- coding: utf-8 -*-

"""
    mundiapi.models.create_card_token_request

    This file was automatically generated by APIMATIC v2.0 ( https://apimatic.io )
"""


class CreateCardTokenRequest(object):

    """Implementation of the 'CreateCardTokenRequest' model.

    Card token data

    Attributes:
        number (string): Credit card number
        holder_name (string): Holder name, as written on the card
        exp_month (int): The expiration month
        exp_year (int): The expiration year, that can be informed with 2 or 4
            digits
        cvv (string): The card's security code
        brand (string): Card brand

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "number":'number',
        "holder_name":'holder_name',
        "exp_month":'exp_month',
        "exp_year":'exp_year',
        "cvv":'cvv',
        "brand":'brand'
    }

    def __init__(self,
                 number=None,
                 holder_name=None,
                 exp_month=None,
                 exp_year=None,
                 cvv=None,
                 brand=None):
        """Constructor for the CreateCardTokenRequest class"""

        # Initialize members of the class
        self.number = number
        self.holder_name = holder_name
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.cvv = cvv
        self.brand = brand


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        number = dictionary.get('number')
        holder_name = dictionary.get('holder_name')
        exp_month = dictionary.get('exp_month')
        exp_year = dictionary.get('exp_year')
        cvv = dictionary.get('cvv')
        brand = dictionary.get('brand')

        # Return an object of this model
        return cls(number,
                   holder_name,
                   exp_month,
                   exp_year,
                   cvv,
                   brand)


