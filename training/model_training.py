import json

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from medical_report_app.config import TRAINED_MODEL_PATH, TRAINING_REPORT_PATH

try:
    import joblib
except ImportError as error:  # pragma: no cover - depends on runtime environment
    raise RuntimeError("joblib is required to save trained models. Install it with `pip install joblib`.") from error

from .dataset_loader import dataset_metadata, load_uci_heart_disease_dataset
from .preprocessing import build_preprocessor


def build_candidate_models():
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=6,
            min_samples_leaf=3,
            random_state=42,
            class_weight="balanced",
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    }

    try:
        from xgboost import XGBClassifier

        candidates["XGBoost"] = XGBClassifier(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
        )
    except ImportError:
        pass

    return candidates


def _evaluate_model(model_pipeline, x_test, y_test):
    predictions = model_pipeline.predict(x_test)
    probabilities = model_pipeline.predict_proba(x_test)[:, 1]
    return {
        "accuracy": round(accuracy_score(y_test, predictions), 4),
        "precision": round(precision_score(y_test, predictions, zero_division=0), 4),
        "recall": round(recall_score(y_test, predictions, zero_division=0), 4),
        "f1": round(f1_score(y_test, predictions, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, probabilities), 4),
    }


def train_and_save_best_model(force_refresh=False):
    dataset = load_uci_heart_disease_dataset(force_refresh=force_refresh)
    x = dataset.drop(columns=["target"]).copy()
    y = dataset["target"].astype(int)

    if "sex" in x.columns:
        x["sex"] = x["sex"].map({1: "male", 0: "female"}).fillna(x["sex"].astype(str))
    if "fbs" in x.columns:
        x["fbs"] = pd.to_numeric(x["fbs"], errors="coerce")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    best_pipeline = None
    best_name = None
    best_metrics = None
    comparison = {}

    for model_name, estimator in build_candidate_models().items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("model", estimator),
            ]
        )
        pipeline.fit(x_train, y_train)
        metrics = _evaluate_model(pipeline, x_test, y_test)
        comparison[model_name] = metrics

        if best_metrics is None or (metrics["roc_auc"], metrics["f1"]) > (best_metrics["roc_auc"], best_metrics["f1"]):
            best_pipeline = pipeline
            best_name = model_name
            best_metrics = metrics

    transformed_feature_names = list(best_pipeline.named_steps["preprocessor"].get_feature_names_out())
    metadata = dataset_metadata()
    metadata.update(
        {
            "best_model_name": best_name,
            "training_rows": int(len(dataset)),
            "feature_columns": list(x.columns),
            "transformed_feature_names": transformed_feature_names,
            "removed_pii_columns": [],
            "explain_background": x_train.head(50).copy(),
        }
    )

    bundle = {
        "pipeline": best_pipeline,
        "metrics": best_metrics,
        "all_model_metrics": comparison,
        "metadata": metadata,
    }
    joblib.dump(bundle, TRAINED_MODEL_PATH)

    report = {
        "selected_model": best_name,
        "metrics": best_metrics,
        "all_model_metrics": comparison,
        "dataset": dataset_metadata(),
    }
    TRAINING_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
