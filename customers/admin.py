from django.contrib import admin
from .models import Customer, CustomerInteraction, LoyaltyProgram, Address

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'date_joined', 'is_loyalty_member', 'loyalty_points')
    list_filter = ('date_joined', 'is_loyalty_member')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined',) 
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Loyalty', {
            'fields': ('is_loyalty_member', 'loyalty_points')
        }),
        ('Dates', {
            'fields': ('date_joined',)  
        }),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_type', 'city', 'country']
    search_fields = ['customer__first_name', 'customer__last_name', 'city']
    list_filter = ['address_type', 'country']

@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'interaction_type', 'interaction_date', 'notes')
    list_filter = ('interaction_type', 'interaction_date')
    search_fields = ('customer__first_name', 'customer__last_name', 'interaction_type')
    ordering = ('-interaction_date',)
    raw_id_fields = ('customer',)


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'tier')
    list_filter = ('tier',)
    search_fields = ('customer__first_name', 'customer__last_name')
    ordering = ('-points',)

