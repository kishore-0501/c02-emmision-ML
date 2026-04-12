from pathlib import Path
import json
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import learning_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

BASE_DIR = Path("/home/ec2-user/environment/supplytrack-ml")
SPLITS_DIR = BASE_DIR / "data" / "model_splits"
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
GRAPHS_DIR = ARTIFACTS_DIR / "graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

REG_TRAIN = SPLITS_DIR / "regression_train.csv"
REG_TEST = SPLITS_DIR / "regression_test.csv"
CLS_TRAIN = SPLITS_DIR / "classification_train.csv"
CLS_TEST = SPLITS_DIR / "classification_test.csv"

COMPARISON_CSV = ARTIFACTS_DIR / "model_comparison.csv"
BEST_SUMMARY_JSON = ARTIFACTS_DIR / "best_model_summary.json"

FEATURE_COLUMNS = [
    "ORIG_STATE",
    "DEST_STATE",
    "SECTOR",
    "SCTG",
    "mode_simple",
    "SHIPMT_VALUE",
    "weight_tonnes",
    "distance_km",
    "tonne_km",
    "is_temp_controlled",
    "is_export",
    "is_hazmat",
]

CATEGORICAL_FEATURES = [
    "ORIG_STATE",
    "DEST_STATE",
    "SECTOR",
    "SCTG",
    "mode_simple",
]

NUMERIC_FEATURES = [
    "SHIPMT_VALUE",
    "weight_tonnes",
    "distance_km",
    "tonne_km",
    "is_temp_controlled",
    "is_export",
    "is_hazmat",
]

REGRESSION_TARGET = "co2_emission_kg"
CLASSIFICATION_TARGET = "high_emission_risk"


def make_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("num", "passthrough", NUMERIC_FEATURES),
        ]
    )


def build_model_by_name(model_name: str):
    if model_name == "Linear Regression":
        model = LinearRegression()
    elif model_name == "Random Forest Regressor":
        model = RandomForestRegressor(
            n_estimators=150,
            max_depth=18,
            random_state=42,
            n_jobs=-1,
        )
    elif model_name == "Gradient Boosting Regressor":
        model = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.05,
            random_state=42,
        )
    elif model_name == "Logistic Regression":
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
        )
    elif model_name == "Random Forest Classifier":
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=18,
            random_state=42,
            n_jobs=-1,
        )
    elif model_name == "Decision Tree Classifier":
        model = DecisionTreeClassifier(
            max_depth=12,
            random_state=42,
        )
    else:
        raise ValueError(f"Unsupported model name: {model_name}")

    return Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            ("model", model),
        ]
    )


def save_plot(filepath: Path):
    plt.tight_layout()
    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    if not REG_TRAIN.exists():
        raise FileNotFoundError(f"Missing file: {REG_TRAIN}")
    if not REG_TEST.exists():
        raise FileNotFoundError(f"Missing file: {REG_TEST}")
    if not CLS_TRAIN.exists():
        raise FileNotFoundError(f"Missing file: {CLS_TRAIN}")
    if not CLS_TEST.exists():
        raise FileNotFoundError(f"Missing file: {CLS_TEST}")
    if not COMPARISON_CSV.exists():
        raise FileNotFoundError(f"Missing file: {COMPARISON_CSV}")
    if not BEST_SUMMARY_JSON.exists():
        raise FileNotFoundError(f"Missing file: {BEST_SUMMARY_JSON}")

    reg_train_df = pd.read_csv(REG_TRAIN)
    reg_test_df = pd.read_csv(REG_TEST)
    cls_train_df = pd.read_csv(CLS_TRAIN)
    cls_test_df = pd.read_csv(CLS_TEST)
    comparison_df = pd.read_csv(COMPARISON_CSV)

    with open(BEST_SUMMARY_JSON, "r") as f:
        summary = json.load(f)

    # ----------------------------
    # 1. Regression model comparison chart
    # ----------------------------
    reg_df = comparison_df[comparison_df["task"] == "regression"].copy()
    reg_df["rmse"] = pd.to_numeric(reg_df["rmse"], errors="coerce")

    plt.figure(figsize=(8, 4.5))
    plt.bar(reg_df["model"], reg_df["rmse"])
    plt.title("Regression Model Comparison (RMSE)")
    plt.xlabel("Model")
    plt.ylabel("RMSE")
    plt.xticks(rotation=15, ha="right")
    save_plot(GRAPHS_DIR / "regression_model_comparison_rmse.png")

    # ----------------------------
    # 2. Classification model comparison chart
    # ----------------------------
    cls_df = comparison_df[comparison_df["task"] == "classification"].copy()
    cls_df["f1"] = pd.to_numeric(cls_df["f1"], errors="coerce")

    plt.figure(figsize=(8, 4.5))
    plt.bar(cls_df["model"], cls_df["f1"])
    plt.title("Classification Model Comparison (F1 Score)")
    plt.xlabel("Model")
    plt.ylabel("F1 Score")
    plt.xticks(rotation=15, ha="right")
    save_plot(GRAPHS_DIR / "classification_model_comparison_f1.png")

    # ----------------------------
    # Prepare train/test data
    # ----------------------------
    X_reg_train = reg_train_df[FEATURE_COLUMNS]
    y_reg_train = reg_train_df[REGRESSION_TARGET]
    X_reg_test = reg_test_df[FEATURE_COLUMNS]
    y_reg_test = reg_test_df[REGRESSION_TARGET]

    X_cls_train = cls_train_df[FEATURE_COLUMNS]
    y_cls_train = cls_train_df[CLASSIFICATION_TARGET]
    X_cls_test = cls_test_df[FEATURE_COLUMNS]
    y_cls_test = cls_test_df[CLASSIFICATION_TARGET]

    # ----------------------------
    # Best model names
    # ----------------------------
    best_reg_model_name = summary.get("best_regression_model", "Random Forest Regressor")
    best_cls_model_name = summary.get("best_classification_model", "Random Forest Classifier")

    best_reg_pipeline = build_model_by_name(best_reg_model_name)
    best_cls_pipeline = build_model_by_name(best_cls_model_name)

    # ----------------------------
    # 3. Learning curve - best regression model
    # ----------------------------
    train_sizes, train_scores, val_scores = learning_curve(
        best_reg_pipeline,
        X_reg_train,
        y_reg_train,
        cv=3,
        scoring="neg_root_mean_squared_error",
        train_sizes=np.linspace(0.2, 1.0, 5),
        n_jobs=1,
    )

    train_rmse = -train_scores.mean(axis=1)
    val_rmse = -val_scores.mean(axis=1)

    plt.figure(figsize=(8, 4.5))
    plt.plot(train_sizes, train_rmse, marker="o", label="Training RMSE")
    plt.plot(train_sizes, val_rmse, marker="o", label="Validation RMSE")
    plt.title(f"Learning Curve - {best_reg_model_name}")
    plt.xlabel("Training Set Size")
    plt.ylabel("RMSE")
    plt.legend()
    save_plot(GRAPHS_DIR / "learning_curve_best_regression.png")

    # ----------------------------
    # 4. Learning curve - best classification model
    # ----------------------------
    train_sizes, train_scores, val_scores = learning_curve(
        best_cls_pipeline,
        X_cls_train,
        y_cls_train,
        cv=3,
        scoring="f1_weighted",
        train_sizes=np.linspace(0.2, 1.0, 5),
        n_jobs=1,
    )

    train_f1 = train_scores.mean(axis=1)
    val_f1 = val_scores.mean(axis=1)

    plt.figure(figsize=(8, 4.5))
    plt.plot(train_sizes, train_f1, marker="o", label="Training F1")
    plt.plot(train_sizes, val_f1, marker="o", label="Validation F1")
    plt.title(f"Learning Curve - {best_cls_model_name}")
    plt.xlabel("Training Set Size")
    plt.ylabel("F1 Score")
    plt.legend()
    save_plot(GRAPHS_DIR / "learning_curve_best_classification.png")

    # ----------------------------
    # Fit best models for test-set plots
    # ----------------------------
    best_reg_pipeline.fit(X_reg_train, y_reg_train)
    best_cls_pipeline.fit(X_cls_train, y_cls_train)

    reg_preds = best_reg_pipeline.predict(X_reg_test)
    cls_preds = best_cls_pipeline.predict(X_cls_test)

    # ----------------------------
    # 5. Actual vs Predicted scatter plot
    # ----------------------------
    plt.figure(figsize=(6, 6))
    plt.scatter(y_reg_test, reg_preds, alpha=0.5)
    diagonal_min = min(y_reg_test.min(), reg_preds.min())
    diagonal_max = max(y_reg_test.max(), reg_preds.max())
    plt.plot([diagonal_min, diagonal_max], [diagonal_min, diagonal_max], linestyle="--")
    plt.title(f"Actual vs Predicted CO₂ - {best_reg_model_name}")
    plt.xlabel("Actual CO₂")
    plt.ylabel("Predicted CO₂")
    save_plot(GRAPHS_DIR / "actual_vs_predicted_co2.png")

    # ----------------------------
    # 6. Residual plot
    # ----------------------------
    residuals = y_reg_test - reg_preds

    plt.figure(figsize=(8, 4.5))
    plt.scatter(reg_preds, residuals, alpha=0.5)
    plt.axhline(0, linestyle="--")
    plt.title(f"Residual Plot - {best_reg_model_name}")
    plt.xlabel("Predicted CO₂")
    plt.ylabel("Residuals")
    save_plot(GRAPHS_DIR / "residual_plot_co2.png")

    # ----------------------------
    # 7. Confusion matrix
    # ----------------------------
    plt.figure(figsize=(6, 6))
    disp = ConfusionMatrixDisplay.from_predictions(
        y_cls_test,
        cls_preds,
        xticks_rotation=30,
    )
    disp.ax_.set_title(f"Confusion Matrix - {best_cls_model_name}")
    save_plot(GRAPHS_DIR / "confusion_matrix_classification.png")

    # ----------------------------
    # 8. Feature importance charts if available
    # ----------------------------
    reg_model = best_reg_pipeline.named_steps["model"]
    reg_preprocessor = best_reg_pipeline.named_steps["preprocessor"]

    if hasattr(reg_model, "feature_importances_"):
        reg_feature_names = reg_preprocessor.get_feature_names_out()
        reg_importance = pd.DataFrame({
            "feature": reg_feature_names,
            "importance": reg_model.feature_importances_,
        }).sort_values("importance", ascending=False).head(15)

        plt.figure(figsize=(8, 5))
        plt.barh(reg_importance["feature"][::-1], reg_importance["importance"][::-1])
        plt.title(f"Top Regression Feature Importances - {best_reg_model_name}")
        plt.xlabel("Importance")
        save_plot(GRAPHS_DIR / "feature_importance_regression.png")

    cls_model = best_cls_pipeline.named_steps["model"]
    cls_preprocessor = best_cls_pipeline.named_steps["preprocessor"]

    if hasattr(cls_model, "feature_importances_"):
        cls_feature_names = cls_preprocessor.get_feature_names_out()
        cls_importance = pd.DataFrame({
            "feature": cls_feature_names,
            "importance": cls_model.feature_importances_,
        }).sort_values("importance", ascending=False).head(15)

        plt.figure(figsize=(8, 5))
        plt.barh(cls_importance["feature"][::-1], cls_importance["importance"][::-1])
        plt.title(f"Top Classification Feature Importances - {best_cls_model_name}")
        plt.xlabel("Importance")
        save_plot(GRAPHS_DIR / "feature_importance_classification.png")

    print(f"Graphs saved in: {GRAPHS_DIR}")


if __name__ == "__main__":
    main()