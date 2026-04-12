from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import ShipmentForm
from .models import Shipment
from .services import predict_shipment


@login_required
def create_shipment(request):
    prediction_data = None

    if request.method == "POST":
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.created_by = request.user

            predicted_co2, risk_level, prediction_source = predict_shipment(shipment)
            shipment.predicted_co2 = predicted_co2
            shipment.risk_level = risk_level
            shipment.save()

            prediction_data = {
                "shipment_id": shipment.id,
                "predicted_co2": shipment.predicted_co2,
                "risk_level": shipment.risk_level,
                "prediction_source": prediction_source,
                "supplier_name": shipment.supplier_name,
                "transport_mode": shipment.get_transport_mode_display(),
                "distance_km": shipment.distance_km,
                "weight_tons": shipment.weight_tons,
            }

            form = ShipmentForm(instance=shipment)
    else:
        form = ShipmentForm()

    return render(
        request,
        "shipments/create_shipment.html",
        {
            "form": form,
            "prediction_data": prediction_data,
        },
    )


@login_required
def shipment_list(request):
    if request.user.is_staff:
        shipments = Shipment.objects.all().order_by("-created_at")
    else:
        shipments = Shipment.objects.filter(created_by=request.user).order_by("-created_at")

    return render(request, "shipments/shipment_list.html", {"shipments": shipments})