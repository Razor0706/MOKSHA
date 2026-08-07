import re

from medical_report_app.constants import REPORT_TYPE_KEYWORDS, TEST_DEFINITIONS

from .text_processing import (
    clean_label_text,
    find_blood_pressure,
    find_numbers,
    keyword_score,
    noisy_text_variant,
    normalize_ocr_text,
    range_score,
)


CONTEXT_PATTERNS = {
    "sugar": re.compile(r"\b(glucose|sugar|fbs|hba1c|a1c)\b", re.IGNORECASE),
    "lipid": re.compile(r"\b(lipid|cholesterol|ldl|hdl|triglycerides?)\b", re.IGNORECASE),
    "renal": re.compile(r"\b(creatinine|kidney|renal|rft|kft|urea|bun|uric|egfr|sodium|potassium)\b", re.IGNORECASE),
    "liver": re.compile(r"\b(liver|lft|alt|sgpt|ast|sgot|alp|bilirubin|albumin|protein)\b", re.IGNORECASE),
    "hematology": re.compile(r"\b(hemoglobin|haemoglobin|cbc|blood count|hb|hgb|wbc|tlc|platelet|plt|rbc|pcv|esr)\b", re.IGNORECASE),
    "thyroid": re.compile(r"\b(thyroid|tsh|free t3|free t4|ft3|ft4)\b", re.IGNORECASE),
    "vitamin": re.compile(r"\b(vitamin|vit|ferritin|iron|calcium|b12)\b", re.IGNORECASE),
    "inflammation": re.compile(r"\b(hscrp|crp|esr|c-reactive)\b", re.IGNORECASE),
    "blood_pressure": re.compile(r"\b(bp|blood pressure|systolic|diastolic|mmhg)\b", re.IGNORECASE),
}


def _has_relevant_context(test_name, clean_text):
    if test_name in {"fasting_glucose", "hba1c"}:
        return bool(CONTEXT_PATTERNS["sugar"].search(clean_text))
    if test_name in {"total_cholesterol", "ldl", "hdl", "triglycerides"}:
        return bool(CONTEXT_PATTERNS["lipid"].search(clean_text))
    if test_name in {"creatinine", "urea", "uric_acid", "egfr", "sodium", "potassium"}:
        return bool(CONTEXT_PATTERNS["renal"].search(clean_text))
    if test_name in {"alt", "ast", "alp", "total_bilirubin", "direct_bilirubin", "albumin", "total_protein"}:
        return bool(CONTEXT_PATTERNS["liver"].search(clean_text))
    if test_name in {"hemoglobin", "wbc", "platelets", "rbc", "hematocrit", "esr"}:
        return bool(CONTEXT_PATTERNS["hematology"].search(clean_text))
    if test_name in {"tsh", "free_t3", "free_t4"}:
        return bool(CONTEXT_PATTERNS["thyroid"].search(clean_text))
    if test_name in {"vitamin_d", "vitamin_b12", "calcium", "iron", "ferritin"}:
        return bool(CONTEXT_PATTERNS["vitamin"].search(clean_text))
    if test_name in {"hscrp"}:
        return bool(CONTEXT_PATTERNS["inflammation"].search(clean_text))
    return True


def _collect_numeric_candidates(lines):
    candidates = []
    for line_index, line in enumerate(lines):
        context = " ".join(lines[max(0, line_index - 1) : min(len(lines), line_index + 2)])
        for value in find_numbers(line):
            candidates.append(
                {
                    "value": value,
                    "line": line,
                    "context": context,
                    "line_index": line_index,
                }
            )
    return candidates


def _extract_blood_pressure(lines):
    best_candidate = None
    best_score = 0.0
    for line_index, line in enumerate(lines):
        reading = find_blood_pressure(line)
        if not reading:
            continue

        context = " ".join(lines[max(0, line_index - 1) : min(len(lines), line_index + 2)])
        score = keyword_score(context, TEST_DEFINITIONS["blood_pressure_systolic"]["keywords"])
        if score > best_score:
            best_score = score
            best_candidate = reading

    if not best_candidate:
        for line in lines:
            reading = find_blood_pressure(line)
            if reading:
                best_candidate = reading
                break

    if not best_candidate:
        return None, None

    return best_candidate


def extract_values(text):
    normalized_text = normalize_ocr_text(text)
    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
    candidates = _collect_numeric_candidates(lines)
    clean_full_text = clean_label_text(normalized_text)

    extracted = {test_name: None for test_name in TEST_DEFINITIONS}
    used_candidate_ids = set()

    systolic, diastolic = _extract_blood_pressure(lines)
    extracted["blood_pressure_systolic"] = systolic
    extracted["blood_pressure_diastolic"] = diastolic

    for test_name, definition in TEST_DEFINITIONS.items():
        if test_name in {"blood_pressure_systolic", "blood_pressure_diastolic"}:
            continue
        if not _has_relevant_context(test_name, clean_full_text):
            continue

        best_candidate = None
        best_score = 0.0
        for candidate_id, candidate in enumerate(candidates):
            if candidate_id in used_candidate_ids:
                continue

            line_score = keyword_score(candidate["line"], definition["keywords"])
            context_score = keyword_score(candidate["context"], definition["keywords"])
            label_strength = max(line_score, context_score * 0.8)

            if label_strength < 0.65:
                continue

            value_strength = range_score(candidate["value"], definition["range"], definition["ideal"])
            score = (label_strength * 0.85) + (value_strength * 0.15)
            if score > best_score:
                best_score = score
                best_candidate = (candidate_id, candidate)

        if best_candidate:
            candidate_id, candidate = best_candidate
            extracted[test_name] = candidate["value"]
            used_candidate_ids.add(candidate_id)

    try:
        print("========== EXTRACTED VALUES FOR DEBUGGING ==========")
        print({k: v for k, v in extracted.items() if v is not None})
        print("====================================================\n")
    except Exception:
        pass
    return extracted


def detect_report_type(text):
    clean_text = clean_label_text(text)
    noisy_text = noisy_text_variant(text)
    report_scores = {}

    for label, keywords in REPORT_TYPE_KEYWORDS.items():
        report_scores[label] = max(keyword_score(clean_text, keywords), keyword_score(noisy_text, keywords))

    matched = [label for label, score in report_scores.items() if score >= 0.70]
    if len(matched) > 1:
        return " + ".join(matched)
    if matched:
        return matched[0]
    return "Comprehensive Biomarker Report"
