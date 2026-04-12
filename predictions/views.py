from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from shipments.models import Shipment


@login_required
def prediction_result(request, shipment_id):
    shipment = get_object_or_404(
        Shipment,
        id=shipment_id,
        created_by=request.user,
    )

    prediction_source = request.session.get("prediction_source", "Unknown")

    return render(
        request,
        "predictions/prediction_result.html",
        {
            "shipment": shipment,
            "prediction_source": prediction_source,
        },
    )