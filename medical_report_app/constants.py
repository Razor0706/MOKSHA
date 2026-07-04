TEST_DEFINITIONS = {
    "fasting_glucose": {
        "label": "Fasting Glucose",
        "unit": "mg/dL",
        "range": (55, 320),
        "ideal": (70, 99),
        "normal_range": "70-99",
        "keywords": [
            "fasting glucose",
            "fasting blood sugar",
            "glucose fasting",
            "blood sugar fasting",
            "blood glucose fasting",
            "glucose",
            "fbs",
            "sugar",
        ],
    },
    "hba1c": {
        "label": "HbA1c",
        "unit": "%",
        "range": (4, 15),
        "ideal": (4.5, 5.6),
        "normal_range": "Below 5.7",
        "keywords": [
            "hba1c",
            "hb a1c",
            "glycated hemoglobin",
            "glycated haemoglobin",
            "glycosylated hemoglobin",
            "glycosylated haemoglobin",
            "a1c",
        ],
    },
    "total_cholesterol": {
        "label": "Total Cholesterol",
        "unit": "mg/dL",
        "range": (80, 400),
        "ideal": (125, 199),
        "normal_range": "Below 200",
        "keywords": ["total cholesterol", "cholesterol total", "serum cholesterol", "cholesterol", "cholester0l"],
    },
    "ldl": {
        "label": "LDL",
        "unit": "mg/dL",
        "range": (40, 280),
        "ideal": (50, 99),
        "normal_range": "Below 100",
        "keywords": ["ldl", "ld1", "low density lipoprotein", "low-density", "ldl cholesterol"],
    },
    "hdl": {
        "label": "HDL",
        "unit": "mg/dL",
        "range": (20, 120),
        "ideal": (40, 80),
        "normal_range": "40 or higher",
        "keywords": ["hdl", "hd1", "high density lipoprotein", "high-density", "hdl cholesterol"],
    },
    "triglycerides": {
        "label": "Triglycerides",
        "unit": "mg/dL",
        "range": (30, 600),
        "ideal": (50, 149),
        "normal_range": "Below 150",
        "keywords": ["triglycerides", "triglyceride", "triglycerid", "tg", "tri glycerides"],
    },
    "blood_pressure_systolic": {
        "label": "Blood Pressure (Systolic)",
        "unit": "mmHg",
        "range": (80, 220),
        "ideal": (90, 119),
        "normal_range": "Below 120",
        "keywords": ["blood pressure", "bp", "b.p", "systolic", "resting blood pressure", "pressure"],
    },
    "blood_pressure_diastolic": {
        "label": "Blood Pressure (Diastolic)",
        "unit": "mmHg",
        "range": (40, 130),
        "ideal": (60, 79),
        "normal_range": "Below 80",
        "keywords": ["blood pressure", "bp", "b.p", "diastolic", "resting blood pressure", "pressure"],
    },
    "creatinine": {
        "label": "Creatinine",
        "unit": "mg/dL",
        "range": (0.3, 12),
        "ideal": (0.6, 1.3),
        "normal_range": "0.6-1.3",
        "keywords": ["creatinine", "serum creatinine", "creat", "creatinin", "creatinine"],
    },
    "hemoglobin": {
        "label": "Hemoglobin",
        "unit": "g/dL",
        "range": (4, 22),
        "ideal": (12, 17.5),
        "normal_range": "12.0-17.5",
        "keywords": ["hemoglobin", "haemoglobin", "hb", "hgb", "haemoglobin level"],
    },
}

DISPLAY_TEST_ORDER = [
    "fasting_glucose",
    "hba1c",
    "total_cholesterol",
    "ldl",
    "hdl",
    "triglycerides",
    "blood_pressure",
    "creatinine",
    "hemoglobin",
]

REPORT_TYPE_KEYWORDS = {
    "Lipid Profile": ["lipid profile", "cholesterol", "triglycerides", "hdl", "ldl"],
    "Blood Sugar Report": ["blood sugar", "fasting glucose", "glucose fasting", "hba1c", "glycated hemoglobin", "fbs"],
    "Kidney Function Report": ["creatinine", "renal profile", "kidney function", "rft", "serum creatinine"],
    "Hematology Report": ["hemoglobin", "haemoglobin", "cbc", "complete blood count"],
}

RISK_ORDER = {"unknown": -1, "low": 0, "moderate": 1, "high": 2}
RISK_LABELS = {
    "unknown": "Unable to Predict",
    "low": "Low Risk",
    "moderate": "Moderate Risk",
    "high": "High Risk",
}

CARDIO_MODEL_FEATURES = ["age", "sex", "trestbps", "chol", "fbs"]
CARDIO_MODEL_FEATURE_LABELS = {
    "age": "Age",
    "sex": "Sex",
    "trestbps": "Resting Blood Pressure",
    "chol": "Total Cholesterol",
    "fbs": "Fasting Blood Sugar Flag",
}

PII_COLUMN_HINTS = [
    "name",
    "address",
    "phone",
    "email",
    "hospital_id",
    "hospitalid",
    "patient_id",
    "patientid",
    "aadhaar",
    "aadhar",
    "ssn",
    "social_security",
    "socialsecurity",
    "report_number",
    "reportnumber",
    "barcode",
    "signature",
    "id",
    "ccf",
]

PRIVACY_NOTICE = (
    "Uploaded reports are processed transiently for extraction and scoring only. "
    "The original file is deleted immediately after analysis, and no personal identifiers are persisted."
)
