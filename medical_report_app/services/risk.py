from medical_report_app.constants import RISK_LABELS, RISK_ORDER

from .ml import predict_lipid_risk


def strongest_risk(*risk_levels):
    return max(risk_levels, key=lambda level: RISK_ORDER[level])


def predict_risk(values):
    glucose = values.get("fasting_glucose")
    cholesterol = values.get("total_cholesterol")
    ldl = values.get("ldl")

    reasons = []
    clinical_risk = "low"

    if glucose is not None:
        if glucose > 126:
            clinical_risk = strongest_risk(clinical_risk, "high")
            reasons.append("Fasting glucose is above 126 mg/dL, which indicates diabetes risk.")
        elif glucose >= 100:
            clinical_risk = strongest_risk(clinical_risk, "moderate")
            reasons.append("Fasting glucose is above the usual healthy fasting range.")

    if cholesterol is not None:
        if cholesterol > 240:
            clinical_risk = strongest_risk(clinical_risk, "high")
            reasons.append("High total cholesterol increases cardiovascular risk.")
        elif cholesterol >= 200:
            clinical_risk = strongest_risk(clinical_risk, "moderate")
            reasons.append("Total cholesterol is elevated and should be monitored.")

    if ldl is not None:
        if ldl > 160:
            clinical_risk = strongest_risk(clinical_risk, "high")
            reasons.append("High LDL cholesterol indicates increased cardiovascular risk.")
        elif ldl >= 130:
            clinical_risk = strongest_risk(clinical_risk, "moderate")
            reasons.append("LDL cholesterol is above the preferred range.")

    ml_risk, confidence = predict_lipid_risk(cholesterol, ldl)
    if ml_risk != "unknown":
        reasons.append(f"The logistic regression model classified the cholesterol and LDL pattern as {RISK_LABELS[ml_risk].lower()}.")

    if not any(value is not None for value in values.values()):
        return {
            "level": RISK_LABELS["unknown"],
            "class_name": "unknown",
            "confidence": None,
            "severity": "unknown",
            "explanation": "Unable to confidently extract values. Please upload a clearer report.",
            "reasons": ["No reliable diagnostic values were detected from the uploaded image."],
            "next_steps": "Upload a clearer image or consult a medical professional with the original report.",
        }

    final_risk = strongest_risk(clinical_risk, ml_risk if ml_risk != "unknown" else "low")
    if final_risk == "low" and not reasons:
        reasons.append("Detected values are within the low-risk range for this prototype.")

    next_steps = {
        "high": "Immediate consultation required.",
        "moderate": "Lifestyle changes and regular monitoring are recommended.",
        "low": "Maintain a healthy lifestyle and continue routine checkups.",
        "unknown": "Upload a clearer report and consult a medical professional.",
    }[final_risk]

    return {
        "level": RISK_LABELS[final_risk],
        "class_name": final_risk,
        "confidence": confidence,
        "severity": final_risk,
        "explanation": " ".join(reasons),
        "reasons": reasons,
        "next_steps": next_steps,
    }


def detect_condition(values, risk):
    glucose = values.get("fasting_glucose")
    cholesterol = values.get("total_cholesterol")
    ldl = values.get("ldl")
    conditions = []

    if glucose is not None and glucose > 126:
        conditions.append("Diabetes Risk")
    if (cholesterol is not None and cholesterol > 240) or (ldl is not None and ldl > 160):
        conditions.append("Cardiovascular Risk")

    if conditions:
        return " + ".join(conditions)
    if risk["severity"] in {"moderate", "high"} and (cholesterol is not None or ldl is not None):
        return "Cardiovascular Risk"
    if risk["severity"] == "unknown":
        return "Insufficient Data"
    return "Normal"


def recommend_specialist(condition):
    specialists = []
    if "Diabetes" in condition:
        specialists.append("Endocrinologist")
    if "Cardiovascular" in condition:
        specialists.append("Cardiologist")

    if specialists:
        return " + ".join(specialists)
    if condition == "Insufficient Data":
        return "Medical Professional"
    return "Routine Physician Follow-up"
