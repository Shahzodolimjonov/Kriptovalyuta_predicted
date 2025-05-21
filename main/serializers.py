from rest_framework import serializers


class PredictionSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    predicted = serializers.ListField(child=serializers.FloatField())
