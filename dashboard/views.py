import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from shipments.models import Shipment
from predictions.ml_service import load_model_comparison, load_best_model_summary


GRAPH_FILENAMES = [
    "regression_model_comparison_rmse.png",
    "classification_model_comparison_f1.png",
    "learning_curve_best_regression.png",
    "learning_curve_best_classification.png",
    "actual_vs_predicted_co2.png",
    "residual_plot_co2.png",
    "confusion_matrix_classification.png",
    "feature_importance_regression.png",
    "feature_importance_classification.png",
]


def format_metric(value, digits=3):
    if value in [None, "", "N/A"]:
        return "N/A"
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return value


def sync_graphs_to_media():
    source_dir = Path(settings.MODEL_DIR) / "graphs"
    target_dir = Path(settings.MEDIA_ROOT) / "graphs"
    target_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []

    if not source_dir.exists():
        return copied_files

    for filename in GRAPH_FILENAMES:
        source_file = source_dir / filename
        target_file = target_dir / filename

        if source_file.exists():
            shutil.copy2(source_file, target_file)
            copied_files.append(filename)

    return copied_files


@login_required
def dashboard_home(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return redirect("user_dashboard")


@login_required
def user_dashboard(request):
    shipments = Shipment.objects.filter(created_by=request.user).order_by("-created_at")

    context = {
        "total_shipments": shipments.count(),
        "recent_shipments": shipments[:5],
    }
    return render(request, "dashboard/user_home.html", context)


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("user_dashboard")

    shipments = Shipment.objects.all().order_by("-created_at")

    total_shipments = shipments.count()
    high_risk_count = shipments.filter(risk_level="High").count()

    avg_co2 = 0
    if shipments.exists():
        co2_values = [float(s.predicted_co2 or 0) for s in shipments]
        avg_co2 = round(sum(co2_values) / len(co2_values), 2)

    comparison_df = load_model_comparison()
    summary = load_best_model_summary() or {}

    reg_best = {}
    cls_best = {}

    if not comparison_df.empty:
        reg_df = comparison_df[comparison_df["task"] == "regression"].copy()
        cls_df = comparison_df[comparison_df["task"] == "classification"].copy()

        if not reg_df.empty:
            reg_best = reg_df.loc[reg_df["rmse"].astype(float).idxmin()].to_dict()

        if not cls_df.empty:
            cls_best = cls_df.loc[cls_df["f1"].astype(float).idxmax()].to_dict()

    comparison_rows = []
    if not comparison_df.empty:
        for _, row in comparison_df.iterrows():
            comparison_rows.append({
                "task": row.get("task", ""),
                "model": row.get("model", ""),
                "mae": format_metric(row.get("mae")),
                "rmse": format_metric(row.get("rmse")),
                "r2": format_metric(row.get("r2")),
                "accuracy": format_metric(row.get("accuracy")),
                "precision": format_metric(row.get("precision")),
                "recall": format_metric(row.get("recall")),
                "f1": format_metric(row.get("f1")),
            })

    context = {
        "total_shipments": total_shipments,
        "avg_co2": avg_co2,
        "high_risk_count": high_risk_count,
        "avg_latency": 0,
        "best_reg_model": reg_best.get("model", summary.get("best_regression_model", "N/A")),
        "best_reg_mae": format_metric(reg_best.get("mae")),
        "best_reg_rmse": format_metric(reg_best.get("rmse")),
        "best_reg_r2": format_metric(reg_best.get("r2")),
        "best_cls_model": cls_best.get("model", summary.get("best_classification_model", "N/A")),
        "best_cls_accuracy": format_metric(cls_best.get("accuracy")),
        "best_cls_precision": format_metric(cls_best.get("precision")),
        "best_cls_recall": format_metric(cls_best.get("recall")),
        "best_cls_f1": format_metric(cls_best.get("f1")),
        "comparison_rows": comparison_rows,
    }

    return render(request, "dashboard/home.html", context)


@login_required
def dashboard_graphs(request):
    if not request.user.is_staff:
        return redirect("user_dashboard")

    copied_files = sync_graphs_to_media()

    graph_titles = {
        "regression_model_comparison_rmse.png": "Regression Model Comparison (RMSE)",
        "classification_model_comparison_f1.png": "Classification Model Comparison (F1 Score)",
        "learning_curve_best_regression.png": "Learning Curve - Best Regression Model",
        "learning_curve_best_classification.png": "Learning Curve - Best Classification Model",
        "actual_vs_predicted_co2.png": "Actual vs Predicted CO₂",
        "residual_plot_co2.png": "Residual Plot - CO₂ Prediction",
        "confusion_matrix_classification.png": "Confusion Matrix - Classification",
        "feature_importance_regression.png": "Feature Importance - Regression",
        "feature_importance_classification.png": "Feature Importance - Classification",
    }

    graph_cards = []
    for filename in copied_files:
        graph_cards.append({
            "title": graph_titles.get(filename, filename),
            "url": f"{settings.MEDIA_URL}graphs/{filename}",
            "filename": filename,
        })

    return render(
        request,
        "dashboard/graphs.html",
        {
            "graph_cards": graph_cards,
        },
    )