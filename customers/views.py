from django.shortcuts import render
from rest_framework import viewsets, generics
from .models import Customer, CustomerInteraction, LoyaltyProgram
from .serializers import CustomerSerializer, CustomerInteractionSerializer, LoyaltyProgramSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-date_joined')
    serializer_class = CustomerSerializer
    filterset_fields = ['city', 'country', 'is_loyalty_member']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']


class CustomerInteractionViewSet(viewsets.ModelViewSet):
    queryset = CustomerInteraction.objects.all().order_by('-interaction_date')
    serializer_class = CustomerInteractionSerializer
    filterset_fields = ['interaction_type']
    search_fields = ['customer__first_name', 'customer__last_name', 'interaction_type']


class LoyaltyProgramViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyProgram.objects.all()
    serializer_class = LoyaltyProgramSerializer
    filterset_fields = ['tier']
    search_fields = ['customer__first_name', 'customer__last_name']

class CustomerListView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerInteractionListView(generics.ListCreateAPIView):
    queryset = CustomerInteraction.objects.all()
    serializer_class = CustomerInteractionSerializer

class LoyaltyProgramView(generics.RetrieveUpdateAPIView):
    queryset = LoyaltyProgram.objects.all()
    serializer_class = LoyaltyProgramSerializer