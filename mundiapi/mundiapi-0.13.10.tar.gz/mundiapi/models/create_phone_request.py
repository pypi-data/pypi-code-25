# -*- coding: utf-8 -*-

"""
    mundiapi.models.create_phone_request

    This file was automatically generated by APIMATIC v2.0 ( https://apimatic.io )
"""


class CreatePhoneRequest(object):

    """Implementation of the 'CreatePhoneRequest' model.

    TODO: type model description here.

    Attributes:
        country_code (string): TODO: type description here.
        number (string): TODO: type description here.
        area_code (string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "country_code":'country_code',
        "number":'number',
        "area_code":'area_code'
    }

    def __init__(self,
                 country_code=None,
                 number=None,
                 area_code=None):
        """Constructor for the CreatePhoneRequest class"""

        # Initialize members of the class
        self.country_code = country_code
        self.number = number
        self.area_code = area_code


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
        country_code = dictionary.get('country_code')
        number = dictionary.get('number')
        area_code = dictionary.get('area_code')

        # Return an object of this model
        return cls(country_code,
                   number,
                   area_code)


