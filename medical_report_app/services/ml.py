from functools import lru_cache

from medical_report_app.config import TRAINED_MODEL_PATH
from medical_report_app.constants import CARDIO_MODEL_FEATURE_LABELS, CARDIO_MODEL_FEATURES, RISK_LABELS

try:
    import joblib
except ImportError:  # pragma: no cover - depends on runtime environment
    joblib = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover - depends on runtime environment
    pd = None


FALLBACK_PROFILE = {
    "age": 54,
    "sex": "male",
    "trestbps": 126,
    "chol": 204,
    "fbs": 0,
}


def _probability_to_level(probability):
    if probability >= 0.67:
        return "high"
    if probability >= 0.38:
        return "moderate"
    return "low"


def _observed_feature_ratio(mapped_features):
    observed = sum(1 for feature in CARDIO_MODEL_FEATURES if mapped_features.get(feature) is not None)
    return observed / len(CARDIO_MODEL_FEATURES)


@lru_cache(maxsize=1)
def load_trained_bundle():
    if joblib is None or not TRAINED_MODEL_PATH.exists():
        return None
    try:
        return joblib.load(TRAINED_MODEL_PATH)
    except Exception:
        return None


def _map_values_to_features(values):
    glucose = values.get("fasting_glucose")
    systolic = values.get("blood_pressure_systolic")
    total_cholesterol = values.get("total_cholesterol")
    age = values.get("age")
    sex = values.get("sex")

    normalized_sex = None
    if isinstance(sex, str):
        lowered = sex.strip().lower()
        if lowered in {"male", "m", "1"}:
            normalized_sex = "male"
        elif lowered in {"female", "f", "0"}:
            normalized_sex = "female"

    return {
        "age": age,
        "sex": normalized_sex,
        "trestbps": systolic,
        "chol": total_cholesterol,
        "fbs": int(glucose > 120) if glucose is not None else None,
    }


def _fallback_explanations(values):
    factors = []
    glucose = values.get("fasting_glucose")
    systolic = values.get("blood_pressure_systolic")
    cholesterol = values.get("total_cholesterol")
    ldl = values.get("ldl")

    if glucose is not None and glucose >= 100:
        factors.append("Fasting glucose is above the healthy baseline.")
    if systolic is not None and systolic >= 130:
        factors.append("Blood pressure is elevated.")
    if cholesterol is not None and cholesterol >= 200:
        factors.append("Total cholesterol is above the desirable range.")
    if ldl is not None and ldl >= 130:
        factors.append("LDL is above the preferred range.")
    return factors[:3]


def _rule_based_ml_fallback(values):
    factors = _fallback_explanations(values)
    probability = 0.18
    if any("glucose" in factor.lower() for factor in factors):
        probability += 0.16
    if any("blood pressure" in factor.lower() for factor in factors):
        probability += 0.18
    if any("cholesterol" in factor.lower() for factor in factors):
        probability += 0.18
    if any("ldl" in factor.lower() for factor in factors):
        probability += 0.18

    probability = min(probability, 0.88)
    level = _probability_to_level(probability)
    confidence = round((55 + (len(factors) * 8)) * (0.75 + (0.25 if factors else 0.0)), 1)
    return {
        "level": level,
        "confidence": confidence,
        "probability": round(probability, 4),
        "top_factors": factors,
        "model_name": "Clinical fallback",
        "model_metrics": {},
        "coverage_ratio": None,
        "used_trained_model": False,
        "summary": "Trained model bundle not found. Falling back to clinically informed heuristic scoring.",
    }


def _recover_feature_name(transformed_name):
    if "__" in transformed_name:
        transformed_name = transformed_name.split("__", 1)[1]
    for base_feature in CARDIO_MODEL_FEATURES:
        if transformed_name == base_feature or transformed_name.startswith(f"{base_feature}_"):
            return base_feature
    return transformed_name


def _shap_explanations(bundle, feature_frame):
    try:
        import shap
    except ImportError:
        return None

    try:
        pipeline = bundle["pipeline"]
        preprocessor = pipeline.named_steps["preprocessor"]
        estimator = pipeline.named_steps["model"]
        background = bundle["metadata"].get("explain_background")
        if background is None or pd is None:
            return None

        transformed = preprocessor.transform(feature_frame)
        background_transformed = preprocessor.transform(background)
        explainer = shap.Explainer(estimator, background_transformed)
        shap_values = explainer(transformed)
        raw_values = shap_values.values[0]
        transformed_names = bundle["metadata"].get("transformed_feature_names", [])

        grouped = {}
        for transformed_name, raw_value in zip(transformed_names, raw_values):
            feature_name = _recover_feature_name(transformed_name)
            grouped[feature_name] = grouped.get(feature_name, 0.0) + abs(float(raw_value))

        ranked = sorted(grouped.items(), key=lambda item: item[1], reverse=True)
        return [CARDIO_MODEL_FEATURE_LABELS.get(name, name) for name, _ in ranked[:3]]
    except Exception:
        return None


def predict_cardiometabolic_risk(values):
    bundle = load_trained_bundle()
    if bundle is None or pd is None:
        return _rule_based_ml_fallback(values)

    mapped_features = _map_values_to_features(values)
    coverage_ratio = _observed_feature_ratio(mapped_features)
    inference_frame = pd.DataFrame([{key: mapped_features.get(key, FALLBACK_PROFILE[key]) for key in CARDIO_MODEL_FEATURES}])

    try:
        pipeline = bundle["pipeline"]
        probability = float(pipeline.predict_proba(inference_frame)[0][1])
        level = _probability_to_level(probability)
        base_confidence = max(probability, 1 - probability) * 100
        confidence = round(base_confidence * (0.65 + (0.35 * coverage_ratio)), 1)
    except Exception:
        return _rule_based_ml_fallback(values)

    factors = _shap_explanations(bundle, inference_frame) or _fallback_explanations(values)
    model_metrics = bundle.get("metrics", {})
    return {
        "level": level,
        "confidence": confidence,
        "probability": round(probability, 4),
        "top_factors": factors,
        "model_name": bundle.get("metadata", {}).get("best_model_name", "Trained cardiometabolic model"),
        "model_metrics": model_metrics,
        "coverage_ratio": round(coverage_ratio, 2),
        "used_trained_model": True,
        "summary": (
            f"{bundle.get('metadata', {}).get('best_model_name', 'The trained model')} estimated "
            f"{RISK_LABELS[level].lower()} from the mapped cardiometabolic markers."
        ),
    }
