from rest_framework import serializers
from .models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class ConvertedValueSerializer(serializers.Serializer):
    converted_value = serializers.FloatField()

    class Meta:
        fields = '__all__'
