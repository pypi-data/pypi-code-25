import json
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='extra.full_name')
    phone_number = serializers.CharField(source='extra.phone_number')
    remote_privileges = serializers.CharField(source='extra.remote_privileges')
    local_privileges = serializers.CharField(source='extra.local_privileges')

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'full_name', 'phone_number', 'remote_privileges', 'local_privileges')


