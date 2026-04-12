from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import ShipmentForm
from .models import Shipment
from .services import predict_shipment


@login_required
def create_shipment(request):
    if request.method == "POST":
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.created_by = request.user

            predicted_co2, risk_level, prediction_source = predict_shipment(shipment)
            shipment.predicted_co2 = predicted_co2
            shipment.risk_level = risk_level
            shipment.save()

            request.session["prediction_source"] = prediction_source
            return redirect("prediction_result", shipment_id=shipment.id)
    else:
        form = ShipmentForm()

    return render(request, "shipments/create_shipment.html", {"form": form})


@login_required
def shipment_list(request):
    shipments = Shipment.objects.filter(created_by=request.user)
    return render(request, "shipments/shipment_list.html", {"shipments": shipments})