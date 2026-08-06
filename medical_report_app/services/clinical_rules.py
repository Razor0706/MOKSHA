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


# --- 1. Glycemic / Diabetic Assessment ---

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


# --- 2. Lipid Profile Assessment ---

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


# --- 3. Cardiovascular & Vitals Assessment ---

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


# --- 4. Kidney Function (KFT / RFT) Assessment ---

def assess_creatinine(value):
    if value is None:
        return _build_result("creatinine", None, "missing", "Not detected", "No reliable creatinine value detected.", "")
    if value < 0.6:
        return _build_result("creatinine", value, "moderate", "Below reference range", "Creatinine is lower than the adult reference floor.", "Low creatinine may relate to reduced muscle mass.")
    if value <= 1.3:
        return _build_result("creatinine", value, "normal", "Within reference range", "Creatinine is within the healthy reference range.", "Normal renal filtration indicator.")
    if value <= 1.9:
        return _build_result("creatinine", value, "moderate", "Mildly elevated", "Creatinine is above the normal reference ceiling.", "Elevated creatinine can reflect reduced kidney filtration or dehydration.")
    return _build_result("creatinine", value, "high", "High", "Creatinine is markedly elevated.", "High creatinine indicates impaired renal clearance requiring clinical evaluation.")


def assess_urea(value):
    if value is None:
        return _build_result("urea", None, "missing", "Not detected", "No reliable urea value detected.", "")
    if value < 7:
        return _build_result("urea", value, "moderate", "Low", "Urea is below typical reference baseline.", "Low urea may occur with low protein intake or liver impairment.")
    if value <= 20:
        return _build_result("urea", value, "normal", "Normal", "Urea is within the normal reference range.", "Normal nitrogenous waste level.")
    if value <= 45:
        return _build_result("urea", value, "moderate", "Mildly elevated", "Urea is slightly above normal baseline.", "Mild elevation can indicate high protein diet or mild dehydration.")
    return _build_result("urea", value, "high", "Elevated", "Urea is markedly elevated.", "Elevated urea suggests impaired renal excretion or catabolic stress.")


def assess_uric_acid(value):
    if value is None:
        return _build_result("uric_acid", None, "missing", "Not detected", "No reliable uric acid value detected.", "")
    if value < 3.5:
        return _build_result("uric_acid", value, "normal", "Low-Normal", "Uric acid is low or low-normal.", "Low uric acid is generally not a clinical concern.")
    if value <= 7.2:
        return _build_result("uric_acid", value, "normal", "Normal", "Uric acid is within normal reference bounds.", "Normal purine metabolism indicator.")
    if value <= 8.5:
        return _build_result("uric_acid", value, "moderate", "Elevated", "Uric acid is above standard reference range.", "Hyperuricemia increases long-term risk of gout or kidney stones.")
    return _build_result("uric_acid", value, "high", "Markedly High", "Uric acid is significantly elevated.", "Marked hyperuricemia warrants clinical evaluation for gout and renal health.")


def assess_egfr(value):
    if value is None:
        return _build_result("egfr", None, "missing", "Not detected", "No reliable eGFR value detected.", "")
    if value >= 90:
        return _build_result("egfr", value, "normal", "Normal", "eGFR indicates normal kidney function.", "Optimal glomerular filtration rate.")
    if value >= 60:
        return _build_result("egfr", value, "moderate", "Mildly decreased", "eGFR indicates mildly reduced kidney function.", "Mild reduction warrants monitoring.")
    if value >= 30:
        return _build_result("egfr", value, "high", "Moderately decreased", "eGFR is moderately reduced.", "Moderate reduction in renal filtration capacity.")
    return _build_result("egfr", value, "high", "Severely decreased", "eGFR is severely reduced.", "Severely reduced eGFR requires immediate nephrology consultation.")


def assess_sodium(value):
    if value is None:
        return _build_result("sodium", None, "missing", "Not detected", "No reliable sodium value detected.", "")
    if value < 135:
        return _build_result("sodium", value, "high", "Low (Hyponatremia)", "Sodium is below normal range.", "Hyponatremia requires clinical assessment.")
    if value <= 145:
        return _build_result("sodium", value, "normal", "Normal", "Sodium is within healthy electrolyte bounds.", "Normal electrolyte balance.")
    return _build_result("sodium", value, "high", "High (Hypernatremia)", "Sodium is above normal range.", "Hypernatremia indicates potential dehydration or fluid imbalance.")


def assess_potassium(value):
    if value is None:
        return _build_result("potassium", None, "missing", "Not detected", "No reliable potassium value detected.", "")
    if value < 3.5:
        return _build_result("potassium", value, "high", "Low (Hypokalemia)", "Potassium is below normal range.", "Hypokalemia can cause muscle weakness or cardiac dysrhythmia.")
    if value <= 5.0:
        return _build_result("potassium", value, "normal", "Normal", "Potassium is within optimal electrolyte range.", "Healthy serum potassium concentration.")
    return _build_result("potassium", value, "high", "High (Hyperkalemia)", "Potassium is elevated.", "Hyperkalemia requires clinical attention due to cardiac safety.")


# --- 5. Liver Function Test (LFT) Assessment ---

def assess_alt(value):
    if value is None:
        return _build_result("alt", None, "missing", "Not detected", "No reliable ALT value detected.", "")
    if value <= 56:
        return _build_result("alt", value, "normal", "Normal", "ALT is within the normal liver enzyme range.", "Normal hepatic transaminase levels.")
    if value <= 150:
        return _build_result("alt", value, "moderate", "Mildly elevated", "ALT is above normal reference baseline.", "Elevated ALT indicates mild liver cell inflammation or fatty liver.")
    return _build_result("alt", value, "high", "High", "ALT is significantly elevated.", "Marked ALT elevation suggests acute liver inflammation or injury.")


def assess_ast(value):
    if value is None:
        return _build_result("ast", None, "missing", "Not detected", "No reliable AST value detected.", "")
    if value <= 40:
        return _build_result("ast", value, "normal", "Normal", "AST is within normal reference limits.", "Normal hepatic enzyme baseline.")
    if value <= 120:
        return _build_result("ast", value, "moderate", "Mildly elevated", "AST is above reference limits.", "Elevated AST can indicate hepatic or muscular stress.")
    return _build_result("ast", value, "high", "High", "AST is markedly elevated.", "High AST indicates significant tissue or liver stress.")


def assess_alp(value):
    if value is None:
        return _build_result("alp", None, "missing", "Not detected", "No reliable ALP value detected.", "")
    if value < 44:
        return _build_result("alp", value, "moderate", "Low", "ALP is below expected reference floor.", "Low ALP can relate to nutritional or metabolic factors.")
    if value <= 147:
        return _build_result("alp", value, "normal", "Normal", "ALP is within standard reference limits.", "Normal biliary and bone enzyme baseline.")
    return _build_result("alp", value, "high", "Elevated", "ALP is elevated.", "Elevated ALP suggests biliary tract or bone turnover involvement.")


def assess_total_bilirubin(value):
    if value is None:
        return _build_result("total_bilirubin", None, "missing", "Not detected", "No reliable total bilirubin value detected.", "")
    if value <= 1.2:
        return _build_result("total_bilirubin", value, "normal", "Normal", "Total bilirubin is within normal range.", "Normal bile pigment processing.")
    if value <= 2.5:
        return _build_result("total_bilirubin", value, "moderate", "Mildly elevated", "Total bilirubin is elevated above baseline.", "Mildly elevated bilirubin merits hepatic evaluation.")
    return _build_result("total_bilirubin", value, "high", "High (Jaundice Risk)", "Total bilirubin is markedly elevated.", "High bilirubin can cause visible jaundice and requires clinical workup.")


def assess_direct_bilirubin(value):
    if value is None:
        return _build_result("direct_bilirubin", None, "missing", "Not detected", "No reliable direct bilirubin value detected.", "")
    if value <= 0.3:
        return _build_result("direct_bilirubin", value, "normal", "Normal", "Direct bilirubin is within expected range.", "Normal conjugated bilirubin handling.")
    return _build_result("direct_bilirubin", value, "high", "Elevated", "Direct bilirubin is elevated.", "Elevated conjugated bilirubin points to post-hepatic or biliary excretion issues.")


def assess_albumin(value):
    if value is None:
        return _build_result("albumin", None, "missing", "Not detected", "No reliable albumin value detected.", "")
    if value < 3.4:
        return _build_result("albumin", value, "moderate", "Low (Hypoalbuminemia)", "Albumin is below healthy reference baseline.", "Low albumin can reflect impaired liver synthesis or protein loss.")
    if value <= 5.4:
        return _build_result("albumin", value, "normal", "Normal", "Albumin is within normal concentration limits.", "Normal protein synthesis indicator.")
    return _build_result("albumin", value, "moderate", "High", "Albumin is above normal baseline.", "Elevated albumin typically relates to dehydration.")


def assess_total_protein(value):
    if value is None:
        return _build_result("total_protein", None, "missing", "Not detected", "No reliable total protein value detected.", "")
    if value < 6.0:
        return _build_result("total_protein", value, "moderate", "Low", "Total protein is below reference baseline.", "Low protein can occur in malabsorption or hepatic underproduction.")
    if value <= 8.3:
        return _build_result("total_protein", value, "normal", "Normal", "Total protein is within normal reference limits.", "Normal serum protein status.")
    return _build_result("total_protein", value, "moderate", "High", "Total protein is elevated.", "High protein may indicate chronic inflammation or dehydration.")


# --- 6. Complete Blood Count (CBC) / Hematology Assessment ---

def assess_hemoglobin(value):
    if value is None:
        return _build_result("hemoglobin", None, "missing", "Not detected", "No reliable hemoglobin value detected.", "")
    if value < 10:
        return _build_result("hemoglobin", value, "high", "Low (Anemia)", "Hemoglobin is clearly below normal adult floor.", "Significant anemia requiring clinical evaluation.")
    if value < 12:
        return _build_result("hemoglobin", value, "moderate", "Borderline low", "Hemoglobin is below healthy adult baseline.", "Mild or borderline anemia.")
    if value <= 17.5:
        return _build_result("hemoglobin", value, "normal", "Within reference range", "Hemoglobin is within healthy adult bounds.", "Normal oxygen-carrying capacity.")
    return _build_result("hemoglobin", value, "moderate", "High", "Hemoglobin is above general adult ceiling.", "High hemoglobin can occur with dehydration or erythrocytosis.")


def assess_wbc(value):
    if value is None:
        return _build_result("wbc", None, "missing", "Not detected", "No reliable WBC count detected.", "")
    if value < 4.5:
        return _build_result("wbc", value, "moderate", "Low (Leukopenia)", "WBC count is below normal reference floor.", "Leukopenia may indicate immune suppression or viral response.")
    if value <= 11.0:
        return _build_result("wbc", value, "normal", "Normal", "WBC count is within normal reference limits.", "Normal immune cell count.")
    if value <= 20.0:
        return _build_result("wbc", value, "high", "Elevated (Leukocytosis)", "WBC count is elevated.", "Leukocytosis suggests active infection or systemic inflammation.")
    return _build_result("wbc", value, "high", "Markedly High", "WBC count is severely elevated.", "Marked leukocytosis requires clinical evaluation for acute infection or hematologic concerns.")


def assess_platelets(value):
    if value is None:
        return _build_result("platelets", None, "missing", "Not detected", "No reliable platelet count detected.", "")
    if value < 150:
        return _build_result("platelets", value, "high", "Low (Thrombocytopenia)", "Platelet count is below normal reference floor.", "Low platelets increase bleeding tendency.")
    if value <= 450:
        return _build_result("platelets", value, "normal", "Normal", "Platelet count is within standard reference range.", "Normal blood clotting cell count.")
    return _build_result("platelets", value, "moderate", "High (Thrombocytosis)", "Platelet count is elevated.", "Elevated platelets can occur with reactive inflammation.")


def assess_rbc(value):
    if value is None:
        return _build_result("rbc", None, "missing", "Not detected", "No reliable RBC count detected.", "")
    if value < 4.2:
        return _build_result("rbc", value, "moderate", "Low", "Red blood cell count is below baseline.", "Low RBC count correlates with anemia.")
    if value <= 5.9:
        return _build_result("rbc", value, "normal", "Normal", "RBC count is within normal limits.", "Normal red cell mass.")
    return _build_result("rbc", value, "moderate", "High", "RBC count is elevated.", "Elevated RBC count may relate to hemoconcentration.")


def assess_hematocrit(value):
    if value is None:
        return _build_result("hematocrit", None, "missing", "Not detected", "No reliable hematocrit value detected.", "")
    if value < 37:
        return _build_result("hematocrit", value, "moderate", "Low", "Hematocrit is below normal percentage.", "Low hematocrit indicates reduced red cell volume fraction.")
    if value <= 52:
        return _build_result("hematocrit", value, "normal", "Normal", "Hematocrit is within healthy range.", "Normal red cell volume fraction.")
    return _build_result("hematocrit", value, "moderate", "High", "Hematocrit is elevated.", "Elevated hematocrit suggests dehydration or polycythemia.")


def assess_esr(value):
    if value is None:
        return _build_result("esr", None, "missing", "Not detected", "No reliable ESR value detected.", "")
    if value <= 20:
        return _build_result("esr", value, "normal", "Normal", "ESR is within normal limits.", "No significant acute phase inflammatory elevation.")
    if value <= 50:
        return _build_result("esr", value, "moderate", "Elevated", "ESR is moderately elevated.", "Elevated ESR points to mild systemic inflammation.")
    return _build_result("esr", value, "high", "Markedly Elevated", "ESR is significantly elevated.", "Marked ESR elevation indicates significant inflammatory activity.")


# --- 7. Thyroid Profile Assessment ---

def assess_tsh(value):
    if value is None:
        return _build_result("tsh", None, "missing", "Not detected", "No reliable TSH value detected.", "")
    if value < 0.45:
        return _build_result("tsh", value, "high", "Low (Suppressed)", "TSH is below healthy reference baseline.", "Low TSH suggests potential hyperthyroidism.")
    if value <= 4.5:
        return _build_result("tsh", value, "normal", "Normal", "TSH is within optimal pituitary-thyroid range.", "Normal thyroid axis function.")
    if value <= 10.0:
        return _build_result("tsh", value, "moderate", "Elevated (Subclinical)", "TSH is above normal reference ceiling.", "Elevated TSH suggests mild or subclinical hypothyroidism.")
    return _build_result("tsh", value, "high", "High (Hypothyroidism)", "TSH is markedly elevated.", "High TSH indicates overt primary hypothyroidism requiring clinical review.")


def assess_free_t3(value):
    if value is None:
        return _build_result("free_t3", None, "missing", "Not detected", "No reliable Free T3 value detected.", "")
    if value < 2.0:
        return _build_result("free_t3", value, "moderate", "Low", "Free T3 is below standard reference range.", "Low FT3 can occur in hypothyroidism or non-thyroidal illness.")
    if value <= 4.4:
        return _build_result("free_t3", value, "normal", "Normal", "Free T3 is within normal metabolic range.", "Normal active thyroid hormone level.")
    return _build_result("free_t3", value, "high", "Elevated", "Free T3 is elevated.", "Elevated FT3 supports hyperthyroid state.")


def assess_free_t4(value):
    if value is None:
        return _build_result("free_t4", None, "missing", "Not detected", "No reliable Free T4 value detected.", "")
    if value < 0.8:
        return _build_result("free_t4", value, "high", "Low", "Free T4 is below normal reference floor.", "Low FT4 indicates decreased thyroid hormone output.")
    if value <= 1.8:
        return _build_result("free_t4", value, "normal", "Normal", "Free T4 is within optimal reference range.", "Normal circulating thyroxine level.")
    return _build_result("free_t4", value, "high", "Elevated", "Free T4 is elevated.", "Elevated FT4 indicates thyroid hormone overproduction.")


# --- 8. Vitamin & Mineral Assessment ---

def assess_vitamin_d(value):
    if value is None:
        return _build_result("vitamin_d", None, "missing", "Not detected", "No reliable Vitamin D value detected.", "")
    if value < 20:
        return _build_result("vitamin_d", value, "high", "Deficient", "Vitamin D is severely deficient (< 20 ng/mL).", "Deficiency affects bone density, immunity, and calcium metabolism.")
    if value < 30:
        return _build_result("vitamin_d", value, "moderate", "Insufficient", "Vitamin D is below optimal sufficiency threshold (20-29 ng/mL).", "Insufficiency warrants supplementation review.")
    if value <= 100:
        return _build_result("vitamin_d", value, "normal", "Sufficient", "Vitamin D is within optimal range (30-100 ng/mL).", "Optimal Vitamin D sufficiency.")
    return _build_result("vitamin_d", value, "moderate", "High", "Vitamin D is above optimal sufficiency range.", "High values should be reviewed if taking high-dose supplements.")


def assess_vitamin_b12(value):
    if value is None:
        return _build_result("vitamin_b12", None, "missing", "Not detected", "No reliable Vitamin B12 value detected.", "")
    if value < 200:
        return _build_result("vitamin_b12", value, "high", "Deficient", "Vitamin B12 is below normal reference floor (< 200 pg/mL).", "B12 deficiency can lead to megaloblastic anemia and neurological symptoms.")
    if value < 300:
        return _build_result("vitamin_b12", value, "moderate", "Borderline Low", "Vitamin B12 is in borderline low range (200-299 pg/mL).", "Borderline B12 merits dietary or supplementation review.")
    if value <= 900:
        return _build_result("vitamin_b12", value, "normal", "Normal", "Vitamin B12 is within healthy reference limits.", "Normal cobalamin status.")
    return _build_result("vitamin_b12", value, "normal", "High", "Vitamin B12 is elevated.", "High B12 is usually benign unless taking parenteral supplements.")


def assess_calcium(value):
    if value is None:
        return _build_result("calcium", None, "missing", "Not detected", "No reliable calcium value detected.", "")
    if value < 8.5:
        return _build_result("calcium", value, "moderate", "Low (Hypocalcemia)", "Serum calcium is below healthy reference baseline.", "Low calcium warrants review of parathyroid and Vitamin D status.")
    if value <= 10.5:
        return _build_result("calcium", value, "normal", "Normal", "Serum calcium is within normal reference limits.", "Normal mineral balance.")
    return _build_result("calcium", value, "high", "Elevated (Hypercalcemia)", "Serum calcium is elevated.", "Elevated calcium warrants clinical workup.")


def assess_iron(value):
    if value is None:
        return _build_result("iron", None, "missing", "Not detected", "No reliable iron value detected.", "")
    if value < 60:
        return _build_result("iron", value, "moderate", "Low", "Serum iron is below standard reference range.", "Low iron is a risk factor for iron deficiency anemia.")
    if value <= 170:
        return _build_result("iron", value, "normal", "Normal", "Serum iron is within expected limits.", "Normal circulating iron levels.")
    return _build_result("iron", value, "moderate", "Elevated", "Serum iron is elevated.", "Elevated serum iron should be interpreted alongside ferritin.")


def assess_ferritin(value):
    if value is None:
        return _build_result("ferritin", None, "missing", "Not detected", "No reliable ferritin value detected.", "")
    if value < 20:
        return _build_result("ferritin", value, "high", "Low (Depleted Iron Stores)", "Ferritin is below reference floor.", "Low ferritin indicates depleted iron reserves.")
    if value <= 250:
        return _build_result("ferritin", value, "normal", "Normal", "Ferritin is within healthy reference range.", "Sufficient body iron reserves.")
    return _build_result("ferritin", value, "moderate", "Elevated", "Ferritin is elevated above normal baseline.", "Elevated ferritin can act as an acute phase inflammatory reactant.")


# --- 9. Inflammatory Assessment ---

def assess_hscrp(value):
    if value is None:
        return _build_result("hscrp", None, "missing", "Not detected", "No reliable hs-CRP value detected.", "")
    if value <= 1.0:
        return _build_result("hscrp", value, "normal", "Low Risk (< 1.0 mg/L)", "hs-CRP indicates low vascular inflammatory risk.", "Low baseline systemic inflammation.")
    if value <= 3.0:
        return _build_result("hscrp", value, "moderate", "Average Risk (1.0-3.0 mg/L)", "hs-CRP indicates moderate vascular inflammatory risk.", "Average systemic inflammatory marker.")
    return _build_result("hscrp", value, "high", "High Inflammatory Risk (> 3.0 mg/L)", "hs-CRP is elevated.", "Elevated hs-CRP indicates systemic inflammation and heightened vascular risk.")


# --- Master Assessment Evaluator ---

def assess_parameters(values):
    assessments = {
        # Glycemic
        "fasting_glucose": assess_fasting_glucose(values.get("fasting_glucose")),
        "hba1c": assess_hba1c(values.get("hba1c")),
        # Lipid
        "total_cholesterol": assess_total_cholesterol(values.get("total_cholesterol")),
        "ldl": assess_ldl(values.get("ldl")),
        "hdl": assess_hdl(values.get("hdl")),
        "triglycerides": assess_triglycerides(values.get("triglycerides")),
        # Vitals
        "blood_pressure": assess_blood_pressure(values),
        # Kidney
        "creatinine": assess_creatinine(values.get("creatinine")),
        "urea": assess_urea(values.get("urea")),
        "uric_acid": assess_uric_acid(values.get("uric_acid")),
        "egfr": assess_egfr(values.get("egfr")),
        "sodium": assess_sodium(values.get("sodium")),
        "potassium": assess_potassium(values.get("potassium")),
        # Liver
        "alt": assess_alt(values.get("alt")),
        "ast": assess_ast(values.get("ast")),
        "alp": assess_alp(values.get("alp")),
        "total_bilirubin": assess_total_bilirubin(values.get("total_bilirubin")),
        "direct_bilirubin": assess_direct_bilirubin(values.get("direct_bilirubin")),
        "albumin": assess_albumin(values.get("albumin")),
        "total_protein": assess_total_protein(values.get("total_protein")),
        # Hematology
        "hemoglobin": assess_hemoglobin(values.get("hemoglobin")),
        "wbc": assess_wbc(values.get("wbc")),
        "platelets": assess_platelets(values.get("platelets")),
        "rbc": assess_rbc(values.get("rbc")),
        "hematocrit": assess_hematocrit(values.get("hematocrit")),
        "esr": assess_esr(values.get("esr")),
        # Thyroid
        "tsh": assess_tsh(values.get("tsh")),
        "free_t3": assess_free_t3(values.get("free_t3")),
        "free_t4": assess_free_t4(values.get("free_t4")),
        # Vitamins
        "vitamin_d": assess_vitamin_d(values.get("vitamin_d")),
        "vitamin_b12": assess_vitamin_b12(values.get("vitamin_b12")),
        "calcium": assess_calcium(values.get("calcium")),
        "iron": assess_iron(values.get("iron")),
        "ferritin": assess_ferritin(values.get("ferritin")),
        # Inflammation
        "hscrp": assess_hscrp(values.get("hscrp")),
    }
    ordered_rows = [assessments[key] for key in DISPLAY_TEST_ORDER if key in assessments]
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
