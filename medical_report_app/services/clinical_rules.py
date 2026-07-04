from medical_report_app.constants import DISPLAY_TEST_ORDER, TEST_DEFINITIONS


SEVERITY_RANK = {"missing": -1, "normal": 0, "low": 1, "moderate": 1, "high": 2}


def _build_result(key, value, severity, status, interpretation, reason):
    return {
        "key": key,
        "label": TEST_DEFINITIONS[key]["label"],
        "value": value,
        "unit": TEST_DEFINITIONS[key]["unit"],
        "normal_range": TEST_DEFINITIONS[key]["normal_range"],
        "severity": severity,
        "status": status,
        "flag_class": severity if severity != "missing" else "missing",
        "interpretation": interpretation,
        "reason": reason,
    }


def assess_fasting_glucose(value):
    if value is None:
        return _build_result("fasting_glucose", None, "missing", "Not detected", "No reliable glucose value detected.", "")
    if value < 70:
        return _build_result("fasting_glucose", value, "moderate", "Low", "Glucose is below the usual fasting range.", "Low fasting glucose may require review if symptoms are present.")
    if value < 100:
        return _build_result("fasting_glucose", value, "normal", "Normal", "Within the usual fasting range.", "Aligned with CDC fasting glucose guidance.")
    if value < 126:
        return _build_result("fasting_glucose", value, "moderate", "Prediabetes range", "Higher than the healthy fasting range.", "Prediabetes-range fasting glucose increases future diabetes risk.")
    return _build_result("fasting_glucose", value, "high", "Diabetes-risk range", "Markedly elevated fasting glucose.", "Fasting glucose at or above 126 mg/dL warrants clinical follow-up.")


def assess_hba1c(value):
    if value is None:
        return _build_result("hba1c", None, "missing", "Not detected", "No reliable HbA1c value detected.", "")
    if value < 5.7:
        return _build_result("hba1c", value, "normal", "Normal", "Within the usual non-diabetic HbA1c range.", "Aligned with CDC HbA1c thresholds.")
    if value < 6.5:
        return _build_result("hba1c", value, "moderate", "Prediabetes range", "HbA1c is above the healthy baseline.", "Prediabetes-range HbA1c may indicate chronic glycemic stress.")
    return _build_result("hba1c", value, "high", "Diabetes-risk range", "HbA1c is markedly elevated.", "HbA1c of 6.5% or above should be reviewed by a clinician.")


def assess_total_cholesterol(value):
    if value is None:
        return _build_result("total_cholesterol", None, "missing", "Not detected", "No reliable total cholesterol value detected.", "")
    if value < 200:
        return _build_result("total_cholesterol", value, "normal", "Desirable", "Total cholesterol is in the desirable range.", "Lower total cholesterol generally reduces cardiovascular burden.")
    if value < 240:
        return _build_result("total_cholesterol", value, "moderate", "Borderline high", "Total cholesterol is above the desirable range.", "Borderline-high total cholesterol should be monitored.")
    return _build_result("total_cholesterol", value, "high", "High", "Total cholesterol is markedly elevated.", "High total cholesterol is associated with higher cardiovascular risk.")


def assess_ldl(value):
    if value is None:
        return _build_result("ldl", None, "missing", "Not detected", "No reliable LDL value detected.", "")
    if value < 100:
        return _build_result("ldl", value, "normal", "Optimal", "LDL is within the optimal range.", "Lower LDL is generally preferred for cardiovascular prevention.")
    if value < 130:
        return _build_result("ldl", value, "moderate", "Near optimal", "LDL is slightly above the optimal target.", "LDL above 100 mg/dL may merit lifestyle review.")
    if value < 160:
        return _build_result("ldl", value, "moderate", "Borderline high", "LDL is above the preferred range.", "Borderline-high LDL increases long-term cardiovascular risk.")
    if value < 190:
        return _build_result("ldl", value, "high", "High", "LDL is significantly elevated.", "High LDL is a major cardiovascular risk contributor.")
    return _build_result("ldl", value, "high", "Very high", "LDL is severely elevated.", "Very high LDL deserves prompt clinical attention.")


def assess_hdl(value):
    if value is None:
        return _build_result("hdl", None, "missing", "Not detected", "No reliable HDL value detected.", "")
    if value < 40:
        return _build_result("hdl", value, "high", "Low", "HDL is below the protective range.", "Low HDL reduces cardiovascular protection.")
    if value < 60:
        return _build_result("hdl", value, "moderate", "Acceptable", "HDL is present but not strongly protective.", "Higher HDL is generally more protective.")
    return _build_result("hdl", value, "normal", "Protective", "HDL is in a protective range.", "Higher HDL is typically associated with lower cardiovascular risk.")


def assess_triglycerides(value):
    if value is None:
        return _build_result("triglycerides", None, "missing", "Not detected", "No reliable triglyceride value detected.", "")
    if value < 150:
        return _build_result("triglycerides", value, "normal", "Normal", "Triglycerides are within the usual range.", "Within the preferred triglyceride range.")
    if value < 200:
        return _build_result("triglycerides", value, "moderate", "Borderline high", "Triglycerides are above the preferred range.", "Borderline-high triglycerides can reflect metabolic strain.")
    if value < 500:
        return _build_result("triglycerides", value, "high", "High", "Triglycerides are significantly elevated.", "High triglycerides raise cardiometabolic concern.")
    return _build_result("triglycerides", value, "high", "Very high", "Triglycerides are severely elevated.", "Very high triglycerides may require urgent review.")


def assess_creatinine(value):
    if value is None:
        return _build_result("creatinine", None, "missing", "Not detected", "No reliable creatinine value detected.", "")
    if value < 0.6:
        return _build_result("creatinine", value, "moderate", "Below reference range", "Creatinine is lower than the general reference range.", "Creatinine should be interpreted with muscle mass and clinical context.")
    if value <= 1.3:
        return _build_result("creatinine", value, "normal", "Within reference range", "Creatinine is within the general adult reference range.", "General reference ranges vary by lab and patient profile.")
    if value <= 1.9:
        return _build_result("creatinine", value, "moderate", "Mildly elevated", "Creatinine is above the general reference range.", "Elevated creatinine can reflect reduced kidney filtration or dehydration.")
    return _build_result("creatinine", value, "high", "High", "Creatinine is markedly elevated.", "High creatinine should be clinically reviewed, especially with symptoms or chronic disease.")


def assess_hemoglobin(value):
    if value is None:
        return _build_result("hemoglobin", None, "missing", "Not detected", "No reliable hemoglobin value detected.", "")
    if value < 10:
        return _build_result("hemoglobin", value, "high", "Low", "Hemoglobin is clearly below the common adult range.", "Low hemoglobin may reflect clinically important anemia.")
    if value < 12:
        return _build_result("hemoglobin", value, "moderate", "Borderline low", "Hemoglobin is below the common adult reference floor.", "WHO adult anemia thresholds are sex-specific, but this value still merits review.")
    if value <= 17.5:
        return _build_result("hemoglobin", value, "normal", "Within reference range", "Hemoglobin is within the common adult reference range.", "Interpret with sex, altitude, and lab reference intervals.")
    return _build_result("hemoglobin", value, "moderate", "High", "Hemoglobin is above the general adult reference range.", "High hemoglobin can occur with dehydration or other conditions.")


def assess_blood_pressure(values):
    systolic = values.get("blood_pressure_systolic")
    diastolic = values.get("blood_pressure_diastolic")
    if systolic is None and diastolic is None:
        return {
            "key": "blood_pressure",
            "label": "Blood Pressure",
            "value": None,
            "unit": "mmHg",
            "normal_range": "Below 120 / 80",
            "severity": "missing",
            "status": "Not detected",
            "flag_class": "missing",
            "interpretation": "No reliable blood pressure value detected.",
            "reason": "",
        }

    value_label = f"{int(systolic) if systolic is not None else '?'}/{int(diastolic) if diastolic is not None else '?'}"
    if systolic is not None and diastolic is not None:
        if systolic < 120 and diastolic < 80:
            severity = "normal"
            status = "Normal"
            interpretation = "Blood pressure is within the normal office range."
            reason = "Consistent with standard ACC/AHA office blood pressure categories."
        elif systolic < 130 and diastolic < 80:
            severity = "moderate"
            status = "Elevated"
            interpretation = "Systolic pressure is above the optimal range."
            reason = "Elevated blood pressure can precede hypertension."
        elif systolic < 140 or diastolic < 90:
            severity = "moderate"
            status = "Hypertension stage 1"
            interpretation = "Blood pressure is in a clinically important elevated range."
            reason = "Stage 1 blood pressure elevation warrants monitoring and clinician review."
        else:
            severity = "high"
            status = "Hypertension stage 2"
            interpretation = "Blood pressure is substantially elevated."
            reason = "Stage 2 blood pressure elevation increases cardiovascular concern."
    else:
        severity = "moderate"
        status = "Partial reading"
        interpretation = "Only one blood pressure component was detected."
        reason = "A complete blood pressure interpretation needs both systolic and diastolic values."

    return {
        "key": "blood_pressure",
        "label": "Blood Pressure",
        "value": value_label,
        "unit": "mmHg",
        "normal_range": "Below 120 / 80",
        "severity": severity,
        "status": status,
        "flag_class": severity,
        "interpretation": interpretation,
        "reason": reason,
    }


def assess_parameters(values):
    assessments = {
        "fasting_glucose": assess_fasting_glucose(values.get("fasting_glucose")),
        "hba1c": assess_hba1c(values.get("hba1c")),
        "total_cholesterol": assess_total_cholesterol(values.get("total_cholesterol")),
        "ldl": assess_ldl(values.get("ldl")),
        "hdl": assess_hdl(values.get("hdl")),
        "triglycerides": assess_triglycerides(values.get("triglycerides")),
        "blood_pressure": assess_blood_pressure(values),
        "creatinine": assess_creatinine(values.get("creatinine")),
        "hemoglobin": assess_hemoglobin(values.get("hemoglobin")),
    }
    ordered_rows = [assessments[key] for key in DISPLAY_TEST_ORDER]
    return assessments, ordered_rows


def strongest_assessment_severity(assessments):
    return max((item["severity"] for item in assessments.values()), key=lambda level: SEVERITY_RANK.get(level, -1))


def abnormal_factor_summaries(assessments, limit=4):
    ranked = sorted(
        (item for item in assessments.values() if item["severity"] in {"moderate", "high"}),
        key=lambda item: (SEVERITY_RANK[item["severity"]], item["label"]),
        reverse=True,
    )
    return [item["reason"] or item["interpretation"] for item in ranked[:limit]]
