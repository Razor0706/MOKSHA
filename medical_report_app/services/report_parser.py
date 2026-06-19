import re

from medical_report_app.constants import TEST_DEFINITIONS

from .text_processing import clean_label_text, find_numbers, keyword_score, noisy_text_variant, normalize_ocr_text, range_score


SUGAR_CONTEXT_PATTERN = re.compile(r"\b(glucose|sugar|fbs)\b")
LIPID_CONTEXT_PATTERN = re.compile(r"\b(lipid|cholesterol|ldl|hdl|triglycerides?)\b")


def extract_values(text):
    normalized_text = normalize_ocr_text(text)
    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
    candidates = []
    clean_full_text = clean_label_text(normalized_text)
    has_sugar_context = bool(SUGAR_CONTEXT_PATTERN.search(clean_full_text))
    has_lipid_context = bool(LIPID_CONTEXT_PATTERN.search(clean_full_text))

    for line_index, line in enumerate(lines):
        for value in find_numbers(line):
            context = " ".join(lines[max(0, line_index - 1) : line_index + 1])
            candidates.append({"value": value, "line": line, "context": context, "line_index": line_index})

    extracted = {test_name: None for test_name in TEST_DEFINITIONS}
    used_candidate_ids = set()

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
