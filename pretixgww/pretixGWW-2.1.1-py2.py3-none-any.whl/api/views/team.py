from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from rest_framework import serializers, generics

from pretix.api.serializers.team import TeamAPITokenSerializer
from pretix.base.models import TeamAPIToken


class TeamTokenAPIView(generics.RetrieveAPIView):
    serializer_class = TeamAPITokenSerializer

    def get_object(self):
        try:
            return TeamAPIToken.objects.get(token=self.kwargs.get('token'), active=1)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('The token does not exist.'))
