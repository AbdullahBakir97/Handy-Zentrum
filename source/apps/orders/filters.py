from django.contrib import admin
from .models import RepairOrder


class UnpaidFilter(admin.SimpleListFilter):
    title = "Unpaid Orders"
    parameter_name = "unpaid"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.unpaid()
        return queryset


class CompletedFilter(admin.SimpleListFilter):
    title = "Completed Orders"
    parameter_name = "completed"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.completed()
        return queryset


class SentToOtherShopFilter(admin.SimpleListFilter):
    title = "Sent to Other Shop"
    parameter_name = "sent_to_other_shop"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.sent_to_other_shop()
        return queryset
