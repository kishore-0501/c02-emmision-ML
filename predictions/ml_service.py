import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings


REGRESSION_MODEL_PATH = Path(settings.MODEL_DIR) / "co2_model.joblib"
CLASSIFICATION_MODEL_PATH = Path(settings.MODEL_DIR) / "risk_model.joblib"
METRICS_PATH = Path(settings.MODEL_DIR) / "metrics.json"
FEATURE_COLUMNS_PATH = Path(settings.MODEL_DIR) / "feature_columns.json"
MODEL_COMPARISON_PATH = Path(settings.MODEL_DIR) / "model_comparison.csv"
BEST_MODEL_SUMMARY_PATH = Path(settings.MODEL_DIR) / "best_model_summary.json"


@lru_cache(maxsize=1)
def load_regression_model():
    if REGRESSION_MODEL_PATH.exists():
        return joblib.load(REGRESSION_MODEL_PATH)
    return None


@lru_cache(maxsize=1)
def load_classification_model():
    if CLASSIFICATION_MODEL_PATH.exists():
        return joblib.load(CLASSIFICATION_MODEL_PATH)
    return None


@lru_cache(maxsize=1)
def load_model_metrics():
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r") as f:
            return json.load(f)
    return {}


@lru_cache(maxsize=1)
def load_feature_columns():
    if FEATURE_COLUMNS_PATH.exists():
        with open(FEATURE_COLUMNS_PATH, "r") as f:
            return json.load(f)
    return []


@lru_cache(maxsize=1)
def load_model_comparison():
    if MODEL_COMPARISON_PATH.exists():
        return pd.read_csv(MODEL_COMPARISON_PATH)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_best_model_summary():
    if BEST_MODEL_SUMMARY_PATH.exists():
        with open(BEST_MODEL_SUMMARY_PATH, "r") as f:
            return json.load(f)
    return {}


def convert_form_input_to_model_features(shipment):
    mode_map = {
        "road": "road",
        "sea": "water",
        "rail": "rail",
        "air": "air",
    }

    mode_simple = mode_map.get(shipment.transport_mode, "road")
    weight_tonnes = float(shipment.weight_tons)
    distance_km = float(shipment.distance_km)
    tonne_km = weight_tonnes * distance_km

    data = {
        "ORIG_STATE": shipment.origin_region,
        "DEST_STATE": shipment.destination_region,
        "SECTOR": shipment.product_category or "General",
        "SCTG": shipment.product_category or "General",
        "mode_simple": mode_simple,
        "SHIPMT_VALUE": float(shipment.shipment_value),
        "weight_tonnes": weight_tonnes,
        "distance_km": distance_km,
        "tonne_km": tonne_km,
        "is_temp_controlled": int(shipment.is_temp_controlled),
        "is_export": int(shipment.is_export),
        "is_hazmat": int(shipment.is_hazmat),
    }

    return data


def predict_shipment_values(shipment):
    regression_model = load_regression_model()
    classification_model = load_classification_model()

    if regression_model is None or classification_model is None:
        return None, None

    input_data = convert_form_input_to_model_features(shipment)
    input_df = pd.DataFrame([input_data])

    predicted_co2 = regression_model.predict(input_df)[0]
    predicted_risk = classification_model.predict(input_df)[0]

    return round(float(predicted_co2), 2), str(predicted_risk)