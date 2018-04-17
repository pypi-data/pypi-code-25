# -*- coding: utf-8 -*-

"""
    mundiapi.models.get_subscription_item_response

    This file was automatically generated by APIMATIC v2.0 ( https://apimatic.io )
"""
from mundiapi.api_helper import APIHelper
import mundiapi.models.get_pricing_scheme_response
import mundiapi.models.get_discount_response
import mundiapi.models.get_subscription_response

class GetSubscriptionItemResponse(object):

    """Implementation of the 'GetSubscriptionItemResponse' model.

    TODO: type model description here.

    Attributes:
        id (string): TODO: type description here.
        description (string): TODO: type description here.
        status (string): TODO: type description here.
        created_at (datetime): TODO: type description here.
        updated_at (datetime): TODO: type description here.
        pricing_scheme (GetPricingSchemeResponse): TODO: type description
            here.
        discounts (list of GetDiscountResponse): TODO: type description here.
        subscription (GetSubscriptionResponse): TODO: type description here.
        name (string): Item name
        quantity (int): TODO: type description here.
        cycles (int): TODO: type description here.
        deleted_at (datetime): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "description":'description',
        "status":'status',
        "created_at":'created_at',
        "updated_at":'updated_at',
        "pricing_scheme":'pricing_scheme',
        "discounts":'discounts',
        "subscription":'subscription',
        "name":'name',
        "quantity":'quantity',
        "cycles":'cycles',
        "deleted_at":'deleted_at'
    }

    def __init__(self,
                 id=None,
                 description=None,
                 status=None,
                 created_at=None,
                 updated_at=None,
                 pricing_scheme=None,
                 discounts=None,
                 subscription=None,
                 name=None,
                 quantity=None,
                 cycles=None,
                 deleted_at=None):
        """Constructor for the GetSubscriptionItemResponse class"""

        # Initialize members of the class
        self.id = id
        self.description = description
        self.status = status
        self.created_at = APIHelper.RFC3339DateTime(created_at) if created_at else None
        self.updated_at = APIHelper.RFC3339DateTime(updated_at) if updated_at else None
        self.pricing_scheme = pricing_scheme
        self.discounts = discounts
        self.subscription = subscription
        self.name = name
        self.quantity = quantity
        self.cycles = cycles
        self.deleted_at = APIHelper.RFC3339DateTime(deleted_at) if deleted_at else None


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
        id = dictionary.get('id')
        description = dictionary.get('description')
        status = dictionary.get('status')
        created_at = APIHelper.RFC3339DateTime.from_value(dictionary.get("created_at")).datetime if dictionary.get("created_at") else None
        updated_at = APIHelper.RFC3339DateTime.from_value(dictionary.get("updated_at")).datetime if dictionary.get("updated_at") else None
        pricing_scheme = mundiapi.models.get_pricing_scheme_response.GetPricingSchemeResponse.from_dictionary(dictionary.get('pricing_scheme')) if dictionary.get('pricing_scheme') else None
        discounts = None
        if dictionary.get('discounts') != None:
            discounts = list()
            for structure in dictionary.get('discounts'):
                discounts.append(mundiapi.models.get_discount_response.GetDiscountResponse.from_dictionary(structure))
        subscription = mundiapi.models.get_subscription_response.GetSubscriptionResponse.from_dictionary(dictionary.get('subscription')) if dictionary.get('subscription') else None
        name = dictionary.get('name')
        quantity = dictionary.get('quantity')
        cycles = dictionary.get('cycles')
        deleted_at = APIHelper.RFC3339DateTime.from_value(dictionary.get("deleted_at")).datetime if dictionary.get("deleted_at") else None

        # Return an object of this model
        return cls(id,
                   description,
                   status,
                   created_at,
                   updated_at,
                   pricing_scheme,
                   discounts,
                   subscription,
                   name,
                   quantity,
                   cycles,
                   deleted_at)


