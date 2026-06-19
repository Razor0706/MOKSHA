from .ocr import extract_text
from .presentation import build_value_rows
from .report_parser import detect_report_type, extract_values
from .risk import detect_condition, predict_risk, recommend_specialist


def analyze_report(filepath):
    ocr_text = extract_text(filepath)
    values = extract_values(ocr_text)
    if not any(value is not None for value in values.values()):
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")

    report_type = detect_report_type(ocr_text)
    risk = predict_risk(values)
    condition = detect_condition(values, risk)
    specialist = recommend_specialist(condition)

    return {
        "report_type": report_type,
        "values": values,
        "value_rows": build_value_rows(values),
        "risk": risk,
        "condition": condition,
        "specialist": specialist,
        "ocr_text": ocr_text,
    }
