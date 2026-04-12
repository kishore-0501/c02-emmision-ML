from django import forms
from .models import Shipment


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            "supplier_name",
            "transport_mode",
            "weight_tons",
            "distance_km",
            "shipment_value",
            "origin_region",
            "destination_region",
            "product_category",
            "is_temp_controlled",
            "is_export",
            "is_hazmat",
        ]
        widgets = {
            "supplier_name": forms.TextInput(attrs={"placeholder": "Enter supplier name"}),
            "transport_mode": forms.Select(),
            "weight_tons": forms.NumberInput(attrs={"placeholder": "e.g. 2.5", "step": "0.01"}),
            "distance_km": forms.NumberInput(attrs={"placeholder": "e.g. 450", "step": "0.01"}),
            "shipment_value": forms.NumberInput(attrs={"placeholder": "e.g. 10000", "step": "0.01"}),
            "origin_region": forms.TextInput(attrs={"placeholder": "e.g. Dublin"}),
            "destination_region": forms.TextInput(attrs={"placeholder": "e.g. Cork"}),
            "product_category": forms.TextInput(attrs={"placeholder": "e.g. Electronics"}),
        }