from django.conf import settings
from django.db import models


class Shipment(models.Model):
    TRANSPORT_MODE_CHOICES = [
        ("road", "Road"),
        ("sea", "Sea"),
        ("rail", "Rail"),
        ("air", "Air"),
    ]

    RISK_LEVEL_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    supplier_name = models.CharField(max_length=150)
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_MODE_CHOICES)

    weight_tons = models.DecimalField(max_digits=10, decimal_places=2)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    shipment_value = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)

    origin_region = models.CharField(max_length=100)
    destination_region = models.CharField(max_length=100)
    product_category = models.CharField(max_length=100, blank=True)

    is_temp_controlled = models.BooleanField(default=False)
    is_export = models.BooleanField(default=False)
    is_hazmat = models.BooleanField(default=False)

    predicted_co2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shipments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.supplier_name} - {self.transport_mode} - {self.created_at.date()}"