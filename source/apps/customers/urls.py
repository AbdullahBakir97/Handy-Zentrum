from django.urls import path

from .views import (
    CustomerDetailView,
    CustomerInteractionListView,
    CustomerListView,
    LoyaltyProgramView,
)

urlpatterns = [
    path("customers/", CustomerListView.as_view(), name="customer-list"),
    path("customers/<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
    path(
        "interactions/",
        CustomerInteractionListView.as_view(),
        name="customer-interaction-list",
    ),
    path("loyalty/<int:pk>/", LoyaltyProgramView.as_view(), name="loyalty-program"),
]
