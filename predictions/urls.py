from django.urls import path
from .views import prediction_result

urlpatterns = [
    path("<int:shipment_id>/", prediction_result, name="prediction_result"),
]