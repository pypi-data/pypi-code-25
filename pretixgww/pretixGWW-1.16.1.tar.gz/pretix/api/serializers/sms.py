from rest_framework import serializers


class OrderDetailSmsSerializer(serializers.Serializer):
    phone = serializers.CharField()
    order = serializers.IntegerField()
    region = serializers.CharField(allow_null=True, allow_blank=True)