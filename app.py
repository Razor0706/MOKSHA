import os
import re
from difflib import SequenceMatcher
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from flask import Flask, render_template, request
from sklearn.linear_model import LogisticRegression
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
UPLOAD_FOLDER.mkdir(exist_ok=True)


# ---------------- ML MODEL ----------------
# Demo dataset generated from common lipid screening thresholds.
# Features: [Total Cholesterol, LDL]
# Classes: 0 = Low, 1 = Moderate, 2 = High
def build_lipid_training_dataset():
    total_cholesterol_values = [145, 160, 175, 190, 199, 205, 215, 225, 235, 240, 255, 275, 300, 330, 365]
    ldl_values = [65, 80, 95, 110, 125, 130, 140, 150, 159, 160, 175, 190, 210, 235]

    samples = []
    labels = []
    for cholesterol in total_cholesterol_values:
        for ldl in ldl_values:
            if cholesterol >= 240 or ldl >= 160:
                label = 2
            elif cholesterol >= 200 or ldl >= 130:
                label = 1
            else:
                label = 0

            samples.append([cholesterol, ldl])
            labels.append(label)

    # Extra boundary cases make the model less brittle near decision cutoffs.
    boundary_examples = [
        ([198, 128], 0),
        ([200, 126], 1),
        ([208, 132], 1),
        ([235, 158], 1),
        ([241, 120], 2),
        ([188, 161], 2),
        ([260, 145], 2),
        ([220, 170], 2),
    ]
    for sample, label in boundary_examples:
        samples.append(sample)
        labels.append(label)

    return np.array(samples), np.array(labels)


X_TRAIN, Y_TRAIN = build_lipid_training_dataset()

model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_TRAIN, Y_TRAIN)


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


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- OCR ----------------
def extract_text(filepath):
    image = cv2.imread(str(filepath))
    if image is None:
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")

    image = cv2.resize(image, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholded = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2,
    )

    text = pytesseract.image_to_string(thresholded, config="--psm 6")
    print("\n========== OCR TEXT FOR DEBUGGING ==========")
    print(text)
    print("===========================================\n")

    if len(text.strip()) < 10:
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")
    return text


# ---------------- TEXT NORMALIZATION ----------------
def normalize_ocr_text(text):
    replacements = {
        "|": "l",
        "\u20b9": "",
        ",": ".",
        ";": ":",
        "\u2014": "-",
        "\u2013": "-",
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text


def noisy_text_variant(text):
    text = normalize_ocr_text(text).lower()
    translation = str.maketrans({"o": "0", "i": "1", "l": "1"})
    return text.translate(translation)


def normalize_numeric_token(token):
    token = token.strip()
    token = token.replace("O", "0").replace("o", "0")
    token = token.replace("I", "1").replace("i", "1").replace("l", "1")
    token = re.sub(r"[^0-9.]", "", token)
    if token.count(".") > 1:
        first_dot = token.find(".")
        token = token[: first_dot + 1] + token[first_dot + 1 :].replace(".", "")
    return token


def clean_label_text(text):
    text = normalize_ocr_text(text).lower()
    text = text.replace("0", "o").replace("1", "l")
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_numbers(line):
    raw_tokens = re.finditer(r"(?<![A-Za-z0-9])[\dOoIiLl]{2,3}(?:[.,][\dOoIiLl]{1,2})?(?![A-Za-z0-9])", line)
    numbers = []
    for match in raw_tokens:
        token = match.group(0)
        prefix = line[max(0, match.start() - 3) : match.start()]
        if "<" in prefix or ">" in prefix:
            continue

        normalized = normalize_numeric_token(token)
        try:
            value = float(normalized)
        except ValueError:
            continue

        if 20 <= value <= 500 and int(value) not in range(1900, 2101):
            numbers.append(value)
    return numbers


def similarity(left, right):
    return SequenceMatcher(None, left, right).ratio()


def keyword_score(text, keywords):
    clean_text = clean_label_text(text)
    tokens = clean_text.split()
    best = 0.0

    for keyword in keywords:
        keyword = clean_label_text(keyword)
        if keyword in clean_text:
            best = max(best, 1.0)

        keyword_parts = keyword.split()
        if len(keyword_parts) > 1:
            window_size = len(keyword_parts)
            for index in range(0, max(1, len(tokens) - window_size + 1)):
                window = " ".join(tokens[index : index + window_size])
                best = max(best, similarity(window, keyword))
        else:
            for token in tokens:
                best = max(best, similarity(token, keyword))

    return best


def range_score(value, expected_range, ideal_range):
    expected_low, expected_high = expected_range
    ideal_low, ideal_high = ideal_range

    if expected_low <= value <= expected_high:
        return 1.0
    if ideal_low <= value <= ideal_high:
        return 0.8

    nearest = expected_low if value < expected_low else expected_high
    distance = abs(value - nearest)
    return max(0.0, 0.55 - (distance / 160))


def extract_values(text):
    normalized_text = normalize_ocr_text(text)
    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
    candidates = []
    clean_full_text = clean_label_text(normalized_text)
    has_sugar_context = bool(re.search(r"\b(glucose|sugar|fbs)\b", clean_full_text))
    has_lipid_context = bool(re.search(r"\b(lipid|cholesterol|ldl|hdl|triglycerides?)\b", clean_full_text))

    for line_index, line in enumerate(lines):
        for value in find_numbers(line):
            context = " ".join(lines[max(0, line_index - 1) : line_index + 1])
            candidates.append({"value": value, "line": line, "context": context, "line_index": line_index})

    extracted = {test_name: None for test_name in TEST_DEFINITIONS}
    used_candidate_ids = set()

    # First pass: fuzzy label matching with OCR-tolerant text.
    for test_name, definition in TEST_DEFINITIONS.items():
        if test_name == "fasting_glucose" and not has_sugar_context:
            continue
        if test_name != "fasting_glucose" and not has_lipid_context:
            continue

        best_candidate = None
        best_score = 0.0

        for candidate_id, candidate in enumerate(candidates):
            if candidate_id in used_candidate_ids:
                continue

            label_strength = keyword_score(candidate["context"], definition["keywords"])
            if label_strength < 0.70:
                continue

            value_strength = range_score(candidate["value"], definition["range"], definition["ideal"])
            score = (label_strength * 0.72) + (value_strength * 0.28)
            if score > best_score:
                best_score = score
                best_candidate = (candidate_id, candidate)

        if best_candidate:
            candidate_id, candidate = best_candidate
            extracted[test_name] = candidate["value"]
            used_candidate_ids.add(candidate_id)

    # Second pass: intelligent range-based fallback for missing values.
    for test_name, definition in TEST_DEFINITIONS.items():
        if extracted[test_name] is not None:
            continue

        if test_name == "fasting_glucose" and not has_sugar_context:
            continue
        if test_name != "fasting_glucose" and not has_lipid_context:
            continue

        best_candidate = None
        best_score = 0.0
        for candidate_id, candidate in enumerate(candidates):
            if candidate_id in used_candidate_ids:
                continue

            value_strength = range_score(candidate["value"], definition["range"], definition["ideal"])
            if value_strength > best_score:
                best_score = value_strength
                best_candidate = (candidate_id, candidate)

        if best_candidate and best_score >= 0.68:
            candidate_id, candidate = best_candidate
            extracted[test_name] = candidate["value"]
            used_candidate_ids.add(candidate_id)

    print("========== EXTRACTED VALUES FOR DEBUGGING ==========")
    print(extracted)
    print("====================================================\n")
    return extracted


def detect_report_type(text):
    clean_text = clean_label_text(text)
    lipid_score = max(
        keyword_score(clean_text, ["lipid profile", "cholesterol", "total cholesterol", "triglycerides"]),
        keyword_score(noisy_text_variant(text), ["lipid profile", "cholesterol", "triglycerides"]),
    )
    sugar_score = max(
        keyword_score(clean_text, ["blood sugar", "fasting glucose", "glucose fasting", "fbs"]),
        keyword_score(noisy_text_variant(text), ["blood sugar", "fasting glucose"]),
    )

    if lipid_score >= 0.82 and sugar_score >= 0.78:
        return "Lipid Profile + Blood Sugar Report"
    if lipid_score >= 0.82:
        return "Lipid Profile"
    if sugar_score >= 0.78:
        return "Blood Sugar Report"
    return "Unknown Report Type"


def ml_lipid_risk(cholesterol, ldl):
    if cholesterol is None or ldl is None:
        return "unknown", None

    prediction = int(model.predict([[cholesterol, ldl]])[0])
    probabilities = model.predict_proba([[cholesterol, ldl]])[0]
    confidence = round(float(np.max(probabilities)) * 100, 1)
    return {0: "low", 1: "moderate", 2: "high"}[prediction], confidence


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

    ml_risk, confidence = ml_lipid_risk(cholesterol, ldl)
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


def format_value(value):
    if value is None:
        return "Not detected"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


def build_value_rows(values):
    rows = []
    for key, definition in TEST_DEFINITIONS.items():
        rows.append(
            {
                "name": definition["label"],
                "value": format_value(values.get(key)),
                "unit": definition["unit"] if values.get(key) is not None else "-",
                "range": f"{definition['range'][0]}-{definition['range'][1]}",
                "detected": values.get(key) is not None,
            }
        )
    return rows


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        return render_template("result.html", error="Please choose a medical report image before uploading.")

    if not allowed_file(uploaded_file.filename):
        return render_template("result.html", error="Only PNG, JPG, and JPEG images are supported.")

    filename = secure_filename(uploaded_file.filename)
    filepath = UPLOAD_FOLDER / filename
    uploaded_file.save(filepath)

    try:
        ocr_text = extract_text(filepath)
        values = extract_values(ocr_text)
        if not any(value is not None for value in values.values()):
            raise ValueError("Unable to confidently extract values. Please upload a clearer report.")

        report_type = detect_report_type(ocr_text)
        risk = predict_risk(values)
        condition = detect_condition(values, risk)
        specialist = recommend_specialist(condition)
    except Exception as error:
        return render_template("result.html", error=str(error))

    return render_template(
        "result.html",
        report_type=report_type,
        values=values,
        value_rows=build_value_rows(values),
        risk=risk,
        condition=condition,
        specialist=specialist,
        ocr_text=ocr_text,
    )


if __name__ == "__main__":
    app.run(debug=True)
