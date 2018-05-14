from pretix.api.serializers.i18n import I18nAwareModelSerializer
from pretix.base.models import Event, TaxRule
from pretix.base.models.event import SubEvent
from pretix.base.models.items import SubEventItem, SubEventItemVariation
from pretix.base.models.pos import Opening_closing_balance
from rest_framework import serializers

class Opening_closing_balanceSerializer(serializers.ModelSerializer):
    """docstring for WholesaleAccountsSerializer"""
    class Meta:
        """docstring for  Meta"""
        model = Opening_closing_balance
        fields = "__all__"
