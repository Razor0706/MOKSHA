from medical_report_app.constants import PRIVACY_NOTICE, RISK_LABELS, RISK_ORDER

from .clinical_rules import abnormal_factor_summaries, assess_parameters, strongest_assessment_severity
from .ml import predict_cardiometabolic_risk


def strongest_risk(*risk_levels):
    return max(risk_levels, key=lambda level: RISK_ORDER[level])


def _clinical_risk_from_assessments(assessments):
    severity = strongest_assessment_severity(assessments)
    if severity == "high":
        return "high"
    if severity in {"moderate", "low"}:
        return "moderate"
    if severity == "normal":
        return "low"
    return "unknown"


def _build_next_steps(final_risk, conditions):
    next_steps = []
    if final_risk == "high":
        next_steps.append("Arrange timely clinician follow-up with the original report.")
        next_steps.append("Repeat or confirm abnormal values through an accredited laboratory if needed.")
    elif final_risk == "moderate":
        next_steps.append("Review lifestyle factors and discuss these markers with a physician soon.")
        next_steps.append("Track repeat measurements if your clinician recommends monitoring.")
    else:
        next_steps.append("Continue routine preventive care and periodic health screening.")

    if "Kidney Function Concern" in conditions or "Renal Clearance Warning" in conditions:
        next_steps.append("Discuss kidney-related markers, hydration status, and medication history with a nephrologist or PCP.")
    if "Possible Anemia" in conditions or "Leukocytosis (Infection Warning)" in conditions:
        next_steps.append("Consider a complete blood count repeat or hematology workup if symptoms persist.")
    if "Hepatic Stress / Enzyme Elevation" in conditions:
        next_steps.append("Discuss liver transaminases, dietary habits, and medication history with a gastroenterologist.")
    if "Thyroid Dysfunction" in conditions:
        next_steps.append("Evaluate thyroid hormone levels (TSH, FT3, FT4) with an endocrinologist.")
    if "Vitamin D / B12 Deficiency" in conditions:
        next_steps.append("Review nutritional supplementation or dietary adjustments with your physician.")
    return next_steps


def predict_risk(values):
    assessments, _ = assess_parameters(values)
    clinical_risk = _clinical_risk_from_assessments(assessments)
    ml_result = predict_cardiometabolic_risk(values)

    available_values = any(value is not None for value in values.values())
    if not available_values:
        return {
            "level": RISK_LABELS["unknown"],
            "class_name": "unknown",
            "ml_level": "unknown",
            "confidence": None,
            "severity": "unknown",
            "explanation": "Unable to confidently extract clinically useful markers from the uploaded report.",
            "reasons": ["No reliable biomarker values were detected from the uploaded image."],
            "top_factors": [],
            "next_steps": ["Upload a clearer report and review the original lab sheet with a qualified clinician."],
            "ml_summary": "No ML inference was attempted because no report values were available.",
            "model_name": "Unavailable",
            "model_metrics": {},
            "privacy_notice": PRIVACY_NOTICE,
            "conditions": ["Insufficient Data"],
        }

    reasons = abnormal_factor_summaries(assessments, limit=6)
    ml_risk = ml_result["level"]
    final_risk = strongest_risk(clinical_risk, ml_risk if ml_risk != "unknown" else "low")

    if ml_result["summary"]:
        reasons.append(ml_result["summary"])

    top_factors = list(ml_result.get("top_factors") or [])
    if not top_factors:
        top_factors = abnormal_factor_summaries(assessments, limit=4)

    if final_risk == "low" and not reasons:
        reasons.append("Detected markers are within low-risk screening ranges for this support tool.")

    conditions = detect_conditions(values, assessments, final_risk, ml_risk)

    explanation = " ".join(reasons)
    confidence = ml_result["confidence"]
    if confidence is None:
        confidence = round(58 + (len(top_factors) * 7), 1)

    return {
        "level": RISK_LABELS[final_risk],
        "class_name": final_risk,
        "ml_level": ml_risk,
        "confidence": confidence,
        "severity": final_risk,
        "explanation": explanation,
        "reasons": reasons,
        "top_factors": top_factors,
        "next_steps": _build_next_steps(final_risk, conditions),
        "ml_summary": ml_result["summary"],
        "model_name": ml_result["model_name"],
        "model_metrics": ml_result["model_metrics"],
        "privacy_notice": PRIVACY_NOTICE,
        "assessments": assessments,
        "conditions": conditions,
    }


def detect_conditions(values, assessments, overall_risk, ml_risk):
    conditions = []

    # Glycemic
    glucose_assessment = assessments["fasting_glucose"]["severity"]
    hba1c_assessment = assessments["hba1c"]["severity"]
    if glucose_assessment in {"moderate", "high"} or hba1c_assessment in {"moderate", "high"}:
        conditions.append("Diabetes Risk")

    # Lipid & Cardiovascular
    lipid_keys = ("total_cholesterol", "ldl", "hdl", "triglycerides")
    if any(assessments[key]["severity"] in {"moderate", "high"} for key in lipid_keys) or assessments["blood_pressure"]["severity"] in {"moderate", "high"}:
        conditions.append("Cardiovascular Risk")

    # Kidney
    kidney_keys = ("creatinine", "urea", "uric_acid", "egfr", "sodium", "potassium")
    if any(assessments[key]["severity"] in {"moderate", "high"} for key in kidney_keys):
        conditions.append("Kidney Function Concern")

    # Liver
    liver_keys = ("alt", "ast", "alp", "total_bilirubin", "direct_bilirubin", "albumin", "total_protein")
    if any(assessments[key]["severity"] in {"moderate", "high"} for key in liver_keys):
        conditions.append("Hepatic Stress / Enzyme Elevation")

    # Hematology
    if assessments["hemoglobin"]["severity"] in {"moderate", "high"}:
        conditions.append("Possible Anemia")
    if assessments["wbc"]["severity"] in {"moderate", "high"}:
        conditions.append("Leukocytosis (Infection Warning)")
    if assessments["platelets"]["severity"] in {"moderate", "high"}:
        conditions.append("Thrombocyte Imbalance")

    # Thyroid
    thyroid_keys = ("tsh", "free_t3", "free_t4")
    if any(assessments[key]["severity"] in {"moderate", "high"} for key in thyroid_keys):
        conditions.append("Thyroid Dysfunction")

    # Vitamins
    vitamin_keys = ("vitamin_d", "vitamin_b12", "calcium", "iron", "ferritin")
    if any(assessments[key]["severity"] in {"moderate", "high"} for key in vitamin_keys):
        conditions.append("Vitamin / Deficiency Caution")

    # Inflammatory
    if assessments["hscrp"]["severity"] in {"moderate", "high"}:
        conditions.append("Systemic Inflammation Warning")

    if not conditions and ml_risk in {"moderate", "high"}:
        conditions.append("Cardiovascular Risk")
    if not conditions and overall_risk == "unknown":
        conditions.append("Insufficient Data")
    if not conditions:
        conditions.append("Normal")
    return conditions


def detect_condition(values, risk):
    assessments = risk.get("assessments")
    if not assessments:
        assessments, _ = assess_parameters(values)
    return " + ".join(detect_conditions(values, assessments, risk["severity"], risk.get("ml_level", "unknown")))


def recommend_specialist(condition):
    specialists = []
    if "Diabetes" in condition:
        specialists.append("Endocrinologist")
    if "Cardiovascular" in condition or "Systemic Inflammation" in condition:
        specialists.append("Cardiologist")
    if "Kidney" in condition:
        specialists.append("Nephrologist")
    if "Hepatic" in condition:
        specialists.append("Gastroenterologist / Hepatologist")
    if "Thyroid" in condition:
        specialists.append("Endocrinologist")
    if "Anemia" in condition or "Leukocytosis" in condition or "Thrombocyte" in condition:
        specialists.append("Hematologist")
    if "Vitamin" in condition:
        specialists.append("General Physician / Nutritionist")

    # Deduplicate while preserving order
    unique_specialists = list(dict.fromkeys(specialists))

    if unique_specialists:
        return " + ".join(unique_specialists)
    if condition == "Insufficient Data":
        return "Medical Professional"
    return "Routine Physician Follow-up"
