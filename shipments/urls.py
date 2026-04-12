from django.urls import path
from .views import create_shipment, shipment_list

urlpatterns = [
    path("", shipment_list, name="shipment_list"),
    path("create/", create_shipment, name="create_shipment"),
]