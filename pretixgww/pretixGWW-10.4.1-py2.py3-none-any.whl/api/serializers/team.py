from pretix.api.serializers.i18n import I18nAwareModelSerializer
from pretix.api.serializers.organizer import OrganizerSerializer
from pretix.base.models import TeamAPIToken, Team


class TeamSerializer(I18nAwareModelSerializer):
    organizer = OrganizerSerializer()

    class Meta:
        model = Team
        fields = '__all__'


class TeamAPITokenSerializer(I18nAwareModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TeamAPIToken
        fields = ('team', 'name', 'token')