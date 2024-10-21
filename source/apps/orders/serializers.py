from rest_framework import serializers
from .models import RepairOrder


class RepairOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
        fields = "__all__"
