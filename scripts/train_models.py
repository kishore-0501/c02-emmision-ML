from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "shipments_sample.csv"
MODEL_DIR = BASE_DIR / "ml_artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

REGRESSION_MODEL_FILE = MODEL_DIR / "co2_model.joblib"
CLASSIFICATION_MODEL_FILE = MODEL_DIR / "risk_model.joblib"

df = pd.read_csv(DATA_FILE)

feature_columns = [
    "supplier_name",
    "transport_mode",
    "weight_tons",
    "distance_km",
    "origin_region",
    "destination_region",
    "product_category",
]

X = df[feature_columns]
y_reg = df["co2_emission"]
y_cls = df["high_emission_risk"]

categorical_features = [
    "supplier_name",
    "transport_mode",
    "origin_region",
    "destination_region",
    "product_category",
]
numeric_features = [
    "weight_tons",
    "distance_km",
]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", "passthrough", numeric_features),
    ]
)

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X, y_reg, test_size=0.2, random_state=42
)

X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(
    X, y_cls, test_size=0.2, random_state=42, stratify=y_cls
)

regression_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(n_estimators=150, random_state=42)),
    ]
)

classification_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", RandomForestClassifier(n_estimators=150, random_state=42)),
    ]
)

regression_pipeline.fit(X_train_reg, y_train_reg)
classification_pipeline.fit(X_train_cls, y_train_cls)

reg_pred = regression_pipeline.predict(X_test_reg)
cls_pred = classification_pipeline.predict(X_test_cls)

mae = mean_absolute_error(y_test_reg, reg_pred)
mse = mean_squared_error(y_test_reg, reg_pred)
rmse = mse ** 0.5
r2 = r2_score(y_test_reg, reg_pred)

accuracy = accuracy_score(y_test_cls, cls_pred)
f1 = f1_score(y_test_cls, cls_pred, average="weighted")

print("\nRegression Metrics")
print("------------------")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

print("\nClassification Metrics")
print("----------------------")
print(f"Accuracy : {accuracy:.4f}")
print(f"F1 Score : {f1:.4f}")

joblib.dump(regression_pipeline, REGRESSION_MODEL_FILE)
joblib.dump(classification_pipeline, CLASSIFICATION_MODEL_FILE)

print(f"\nSaved regression model to: {REGRESSION_MODEL_FILE}")
print(f"Saved classification model to: {CLASSIFICATION_MODEL_FILE}")