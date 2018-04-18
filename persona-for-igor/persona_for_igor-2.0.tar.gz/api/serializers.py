from rest_framework import serializers
from newtable.models import Account, Hub, PersonasToHubs
from personas.models import FeederProcessedArticlesUrls
class FeederProcessedArticlesUrlsSerializer(serializers.ModelSerializer):
    class Meta :
        model = FeederProcessedArticlesUrls
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('id','email')

    def create(self, validated_data):
        obj = Account.objects.create(**validated_data)
        return obj

class HubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hub
        fields = ('id','account','hub_name','api_user_name','api_password')

        # write_only_field = ('brand_id','model_id')

    def create(self, validated_data):
        obj = Hub.objects.create(**validated_data)
        return obj

class PersonasToHubsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonasToHubs
        fields = ('id','personas','hub')

        # write_only_field = ('brand_id','model_id')

    def create(self, validated_data):
        obj = PersonasToHubs.objects.create(**validated_data)
        return obj