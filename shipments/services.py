from decimal import Decimal

from predictions.ml_service import predict_shipment_values


EMISSION_FACTORS = {
    "road": Decimal("0.15"),
    "sea": Decimal("0.008"),
    "rail": Decimal("0.03"),
    "air": Decimal("0.65"),
}


def calculate_baseline_co2(weight_tons, distance_km, transport_mode):
    factor = EMISSION_FACTORS.get(transport_mode, Decimal("0.15"))
    co2 = Decimal(weight_tons) * Decimal(distance_km) * factor
    return round(co2, 2)


def classify_risk(predicted_co2):
    predicted_co2 = Decimal(predicted_co2)

    if predicted_co2 < Decimal("100"):
        return "Low"
    elif predicted_co2 < Decimal("300"):
        return "Medium"
    return "High"


def predict_shipment(shipment):
    try:
        predicted_co2, predicted_risk = predict_shipment_values(shipment)

        if predicted_co2 is not None and predicted_risk is not None:
            return Decimal(str(predicted_co2)), predicted_risk, "ML Model"

    except Exception as e:
        print(f"ML prediction failed, falling back to baseline: {e}")

    baseline_co2 = calculate_baseline_co2(
        shipment.weight_tons,
        shipment.distance_km,
        shipment.transport_mode,
    )
    baseline_risk = classify_risk(baseline_co2)

    return Decimal(str(baseline_co2)), baseline_risk, "Baseline Formula"