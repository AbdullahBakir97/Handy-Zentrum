from django.contrib import admin
from django.contrib import admin
from .models import Shipment, LogisticsInteraction, ReturnShipment
from django.utils import timezone



class LogisticsInteractionInline(admin.TabularInline):
    model = LogisticsInteraction
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['interaction_type', 'notes', 'timestamp']

class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'product', 'quantity', 'status', 'shipped_date', 'estimated_arrival', 'is_on_time', 'shipping_company']
    list_filter = ['status', 'shipping_company', 'shipped_date', 'estimated_arrival']
    search_fields = ['tracking_number', 'product__name', 'origin__name', 'destination']
    inlines = [LogisticsInteractionInline]
    ordering = ['-shipped_date']
    readonly_fields = ['created_at']
    actions = ['mark_as_delivered', 'mark_as_in_transit']

    def is_on_time(self, obj):
        return obj.estimated_arrival >= timezone.now()
    is_on_time.boolean = True
    is_on_time.short_description = 'On Time'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} shipments marked as Delivered.')
    mark_as_delivered.short_description = 'Mark selected shipments as Delivered'

    def mark_as_in_transit(self, request, queryset):
        updated = queryset.update(status='in_transit')
        self.message_user(request, f'{updated} shipments marked as In Transit.')
    mark_as_in_transit.short_description = 'Mark selected shipments as In Transit'

class LogisticsInteractionAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'interaction_type', 'timestamp', 'notes']
    search_fields = ['shipment__tracking_number', 'interaction_type']
    list_filter = ['interaction_type', 'timestamp']

class ReturnShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status', 'reason', 'received_at']
    list_filter = ['status', 'received_at']
    search_fields = ['shipment__tracking_number', 'reason']

admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(LogisticsInteraction, LogisticsInteractionAdmin)
admin.site.register(ReturnShipment, ReturnShipmentAdmin)
