from rest_framework import serializers
from .models import Customer, Address, CustomerInteraction, LoyaltyProgram

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'address_line_1', 'address_line_2', 'city', 'country', 'postal_code']

class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    interaction_count = serializers.IntegerField(source='customer_interactions.count', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'date_joined', 
                  'is_loyalty_member', 'loyalty_points', 'addresses', 'interaction_count']

class CustomerInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInteraction
        fields = ['id', 'customer', 'interaction_type', 'interaction_date', 'notes']

class LoyaltyProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyProgram
        fields = ['id', 'customer', 'points', 'tier']
