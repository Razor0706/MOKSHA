TEST_DEFINITIONS = {
    "fasting_glucose": {
        "label": "Fasting Glucose",
        "unit": "mg/dL",
        "range": (70, 200),
        "ideal": (70, 99),
        "keywords": [
            "fasting glucose",
            "fasting blood sugar",
            "blood sugar fasting",
            "glucose fasting",
            "glucose",
            "fbs",
            "sugar",
        ],
    },
    "total_cholesterol": {
        "label": "Total Cholesterol",
        "unit": "mg/dL",
        "range": (200, 400),
        "ideal": (125, 200),
        "keywords": ["total cholesterol", "cholesterol total", "cholesterol", "cholester0l"],
    },
    "ldl": {
        "label": "LDL",
        "unit": "mg/dL",
        "range": (100, 250),
        "ideal": (50, 130),
        "keywords": ["ldl", "ld1", "low density lipoprotein", "low-density"],
    },
    "hdl": {
        "label": "HDL",
        "unit": "mg/dL",
        "range": (40, 100),
        "ideal": (40, 80),
        "keywords": ["hdl", "hd1", "high density lipoprotein", "high-density"],
    },
    "triglycerides": {
        "label": "Triglycerides",
        "unit": "mg/dL",
        "range": (50, 200),
        "ideal": (50, 150),
        "keywords": ["triglycerides", "triglyceride", "triglycerid", "tg", "tri glycerides"],
    },
}

RISK_ORDER = {"unknown": -1, "low": 0, "moderate": 1, "high": 2}
RISK_LABELS = {
    "unknown": "Unable to Predict",
    "low": "Low Risk",
    "moderate": "Moderate Risk",
    "high": "High Risk",
}
